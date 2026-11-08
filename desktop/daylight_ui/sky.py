"""Small, offline solar and lunar estimates for Daylight.

Copyright (C) 2026 Hamdy Abou El Anein. SPDX-License-Identifier: GPL-3.0-only

Solar equations: NOAA's published fractional-year approximation:
https://gml.noaa.gov/grad/solcalc/solareqns.PDF
This is the compact approximation, not the higher precision Meeus calculator.
Sunrise uses a 90.833 degree zenith, a level horizon and standard refraction;
mountains, elevation and weather are not modelled. Allow several minutes of
error, and substantially more near the polar circles.

The Moon uses a mean 29.530588 day synodic month from the 2000-01-06 18:14 UTC
new moon. NASA's phase tables explain that individual lunations vary:
https://eclipse.gsfc.nasa.gov/phase/phases1901.html
https://eclipse.gsfc.nasa.gov/phase/phases2001.html
Lunar phase, illumination and the next full moon are approximate educational
estimates (potentially a day away), not an astronomical ephemeris.

No network, location lookup or third-party Python dependency is used.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta, timezone
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc
SYNODIC_MONTH = 29.530588
NEW_MOON_EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
PHASE_NAMES = (
    "New moon", "Waxing crescent", "First quarter", "Waxing gibbous",
    "Full moon", "Waning gibbous", "Last quarter", "Waning crescent",
)


def _validate_day(day: date) -> date:
    if not isinstance(day, date):
        raise ValueError("Date must be a calendar date")
    if isinstance(day, datetime):
        day = day.date()
    if not 1900 <= day.year <= 2100:
        raise ValueError("Choose a date between 1900 and 2100 for these estimates")
    return day


def _parameters(moment: datetime) -> tuple[float, float]:
    """Equation of time in minutes and solar declination in radians."""
    moment = moment.astimezone(UTC)
    days_in_year = 366 if calendar.isleap(moment.year) else 365
    day_number = moment.timetuple().tm_yday
    hour = moment.hour + moment.minute / 60 + moment.second / 3600
    gamma = 2 * math.pi / days_in_year * (day_number - 1 + (hour - 12) / 24)
    eqtime = 229.18 * (
        0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma)
    )
    return eqtime, decl


def calculate_sun(day: date, latitude: float, longitude: float,
                  timezone_name: str = "UTC") -> dict:
    """Estimate sunrise/set for the solar day whose noon falls on ``day``.

    Longitude is positive east. Results are timezone-aware datetimes using
    IANA timezone rules, including the offset at each event. At high latitudes
    sunrise can fall on the preceding civil date or sunset on the following
    one. During polar day/night both event fields are None and day length is
    respectively 24 or 0 hours. ``timezone_name`` is selected explicitly by the
    user and is not inferred from coordinates.
    """
    day = _validate_day(day)
    try:
        latitude, longitude = float(latitude), float(longitude)
    except (TypeError, ValueError) as exc:
        raise ValueError("Latitude and longitude must be numbers") from exc
    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, TypeError, ValueError) as exc:
        raise ValueError("Use an IANA timezone, for example Europe/Zurich") from exc
    # UTC arithmetic followed by astimezone handles DST at the event instead
    # of assuming today's UTC offset or hard-coding an extra summer hour.
    base = datetime.combine(day, time(), UTC)
    noon = base + timedelta(minutes=720 - 4 * longitude)
    eqtime, _ = _parameters(noon)
    noon -= timedelta(minutes=eqtime)
    difference = (day - noon.astimezone(zone).date()).days
    base += timedelta(days=difference)
    for _ in range(2):
        eqtime, decl = _parameters(noon)
        noon = base + timedelta(minutes=720 - 4 * longitude - eqtime)
    # Recompute declination at the refined transit instant.
    _, decl = _parameters(noon)
    lat = math.radians(latitude)
    numerator = math.cos(math.radians(90.833)) - math.sin(lat) * math.sin(decl)
    denominator = math.cos(lat) * math.cos(decl)
    if abs(denominator) < 1e-12:
        hour_cos = -math.inf if numerator < 0 else math.inf
    else:
        hour_cos = numerator / denominator
    result = {
        "sunrise": None,
        "sunset": None,
        "solar_noon": noon.astimezone(zone),
        "day_length_hours": 0.0,
        "polar_state": None,
        "approximate": True,
        "timezone": timezone_name,
    }
    if hour_cos < -1:
        result.update(polar_state="polar_day", day_length_hours=24.0)
    elif hour_cos > 1:
        result.update(polar_state="polar_night", day_length_hours=0.0)
    else:
        half_day_minutes = 4 * math.degrees(math.acos(max(-1, min(1, hour_cos))))
        result.update(
            sunrise=(noon - timedelta(minutes=half_day_minutes)).astimezone(zone),
            sunset=(noon + timedelta(minutes=half_day_minutes)).astimezone(zone),
            day_length_hours=2 * half_day_minutes / 60,
        )
    return result


def calculate_moon(day: date | datetime) -> dict:
    """Return a labelled mean-cycle estimate, sampled at UTC noon for a date.

    A timezone-aware datetime can be passed instead to sample that instant.
    The returned next full moon is strictly later than the sampled instant.
    """
    _validate_day(day)
    if isinstance(day, datetime):
        if day.tzinfo is None or day.utcoffset() is None:
            raise ValueError("A datetime must include its timezone")
        moment = day.astimezone(UTC)
    else:
        moment = datetime.combine(day, time(12), UTC)
    elapsed = (moment - NEW_MOON_EPOCH).total_seconds() / 86400
    cycles = elapsed / SYNODIC_MONTH
    phase = cycles % 1
    full_cycle = math.floor(cycles - 0.5) + 1.5
    next_full = NEW_MOON_EPOCH + timedelta(days=full_cycle * SYNODIC_MONTH)
    # Microsecond rounding at a full-moon boundary must still return a future event.
    if next_full <= moment:
        next_full += timedelta(days=SYNODIC_MONTH)
    return {
        "phase_fraction": phase,
        "illumination": (1 - math.cos(2 * math.pi * phase)) / 2,
        "phase_name": PHASE_NAMES[int(phase * 8 + 0.5) % 8],
        "age_days": phase * SYNODIC_MONTH,
        "next_full_moon": next_full,
        "approximate": True,
        "sampled_at": moment,
    }
