#!/usr/bin/env python3
"""Launch the local Daylight desktop library.

Copyright (C) 2026 Hamdy Abou El Anein
SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
import os
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application",nargs="?",default="home")
    parser.add_argument("--first-run",action="store_true")
    parser.add_argument("--session-appearance",action="store_true")
    args=parser.parse_args()
    if os.geteuid()==0 and os.environ.get("DAYLIGHT_DISPOSABLE_TEST")!="yes":
        parser.error("Run graphical applications as the desktop user, not root")
    try:
        from daylight_ui.shell import main as run,appearance_session
        if args.session_appearance:
            appearance_session()
            return 0
        return run(args.application,args.first_run)
    except ImportError as error:
        print(f"Daylight desktop could not start: {error}. Install python3-tk.",file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
