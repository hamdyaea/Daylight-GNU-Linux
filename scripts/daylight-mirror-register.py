#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Operator-reviewed opt-in mirror registration. Health monitor publishes after 24h."""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import socket
from urllib.parse import urlparse

def validate(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
        raise ValueError("HTTPS hostname and optional path only")
    if not "." in parsed.hostname or parsed.hostname == "localhost":
        raise ValueError("Invalid mirror hostname")
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(info[4][0]).is_global for info in addresses):
        raise ValueError("Only publicly routed IPs are accepted")
    return url.rstrip("/")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("/var/lib/daylight-mirrors/registry.json"))
    parser.add_argument("--url", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    if not re.fullmatch("[A-Z]{2}", args.country):
        parser.error("Country must be a two-letter ISO country code")
    if not 1 <= len(args.name) <= 80 or any(ord(c) < 32 for c in args.name):
        parser.error("Invalid display name")
    url = validate(args.url)
    records = json.loads(args.registry.read_text()) if args.registry.exists() else []
    if any(entry["url"].rstrip("/") == url for entry in records):
        parser.error("Mirror already registered")
    records.append({"url":url,"country":args.country,"name":args.name,"healthy_since":None,"failures":0})
    tmp = args.registry.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records,indent=2)+"\n")
    tmp.replace(args.registry)
    print("Registered for monitoring; publication follows 24 consecutive hours of healthy checks:",url)

if __name__ == "__main__":
    main()
