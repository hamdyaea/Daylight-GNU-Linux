-- Daylight-owned entry point; the session-defaults package remains untouched.
-- SPDX-License-Identifier: GPL-3.0-only
dofile(assert(os.getenv('DAYLIGHT_CONKY_CONFIG')))
conky.config.own_window_type = 'override'
