#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Notify the Daylight maintainer of new community mirror requests on GitHub."""
import argparse
from email.message import EmailMessage
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request

API = "https://api.github.com/repos/hamdyaea/Daylight-GNU-Linux/issues?state=all&per_page=100"
def get_issues():
    req = urllib.request.Request(API, headers={"Accept":"application/vnd.github+json","User-Agent":"DaylightMirrorNotifier/1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def requests_from(issues):
    return sorted(
        (i for i in issues if "pull_request" not in i and
         i.get("title", "").lower().startswith("[mirror] ") and
         i.get("html_url", "").startswith("https://github.com/hamdyaea/Daylight-GNU-Linux/issues/")),
        key=lambda i:i["number"])

def send_notification(issue, recipient, sender, dry_run=False):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = f"[Daylight] Nouvelle demande de miroir #{issue['number']}"
    msg.set_content(
        "Une nouvelle demande de miroir APT Daylight GNU/Linux est arrivée.\n\n"
        f"Numéro : #{issue['number']}\n"
        f"Titre : {issue['title']}\n"
        f"Demandeur GitHub : {issue.get('user',{}).get('login','inconnu')}\n"
        f"Lien : {issue['html_url']}\n\n"
        "Vérifie la propriété du domaine et le consentement avant toute inscription.\n"
        "Le miroir ne sera publié qu'après 24 heures de contrôles réussis.\n"
    )
    if dry_run:
        print(msg.as_string())
        return
    subprocess.run(["/usr/sbin/sendmail","-t","-oi"],input=msg.as_bytes(),check=True,timeout=30)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--state",type=Path,default=Path("/var/lib/daylight-mirrors/notified-issues.json"))
    p.add_argument("--to",default=os.getenv("DAYLIGHT_MIRROR_NOTIFY_TO","info@daylightlinux.ch"))
    p.add_argument("--from-address",default="info@daylightlinux.ch")
    p.add_argument("--dry-run",action="store_true")
    p.add_argument("--initialize",action="store_true",help="Mark existing issues as seen without emailing")
    a=p.parse_args()
    issues=requests_from(get_issues())
    seen=set(json.loads(a.state.read_text())) if a.state.exists() else set()
    if a.initialize:
        seen.update(str(i["number"]) for i in issues)
    else:
        for issue in issues:
            ident=str(issue["number"])
            if ident in seen: continue
            send_notification(issue,a.to,a.from_address,a.dry_run)
            if not a.dry_run:
                seen.add(ident)
    if not a.dry_run:
        a.state.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=a.state.parent,prefix=".notified-",text=True)
        try:
            with os.fdopen(fd,"w") as f:
                json.dump(sorted(seen),f)
                f.write("\n")
            os.replace(tmp,a.state)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    print(f"Checked {len(issues)} mirror requests; recorded {len(seen)} notifications")

if __name__=="__main__":
    main()