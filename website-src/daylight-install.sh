#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
# Download, inspect, then execute. A plan is printed unless --yes is explicit.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
BASE=https://daylightlinux.ch/apt
FINGERPRINT=B0575F821A31DD20753DE07C50D21240F4BCB02E
mode=core
games=no
apply=no
usage() {
    printf '%s\n' 'Daylight GNU/Linux installer (Debian 12/13 and compatible ARM64 systems)' 'Usage: sh daylight-install.sh [--all|--desktop|--core|--repo-only|--remove-repo] [--games] [--yes|--plan]' '--all: install the full desktop, applications and all games (no telemetry).' 'Default: show the core-only installation plan; no changes.' 'Desktop mode selects Daylight for the invoking desktop user and offers a reboot.' 'Telemetry is never installed or enabled by this script.'
}
for argument in "$@"; do
    case "$argument" in
        --all) mode=desktop; games=yes ;;
        --core) mode=core ;;
        --desktop) mode=desktop ;;
        --remove-repo) mode=remove_repo ;;
        --repo-only) mode=repo ;;
        --games) games=yes ;;
        --yes) apply=yes ;;
        --plan|--dry-run) apply=no ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$argument" >&2; exit 2 ;;
    esac
done
if [ "$games" = yes ] && [ "$mode" != desktop ]; then echo '--games requires --desktop' >&2; exit 2; fi
command -v dpkg >/dev/null 2>&1 || { echo 'This installer is only for Debian-based systems, not Arch/Manjaro.' >&2; exit 2; }
[ -r /etc/debian_version ] || { echo 'No Debian base detected; no changes made.' >&2; exit 2; }
arch=$(dpkg --print-architecture)
case "$arch" in amd64|arm64) ;; *) echo 'Supported architectures: amd64 and arm64 only.' >&2; exit 2 ;; esac
write_repo_cleanup() {
    cat <<'DAYLIGHT_REPO_CLEANUP'
#!/bin/sh
# Managed by Daylight GNU/Linux installer
set -eu
state=/var/lib/daylight-apt-lifecycle
hook=/etc/dpkg/dpkg.cfg.d/90-daylight-repository
source=/etc/apt/sources.list.d/daylight.sources
pin=/etc/apt/preferences.d/daylight
mirrors=/etc/apt/mirrors/daylight.list
key=/etc/apt/keyrings/daylight-archive-keyring.gpg

# A missing package and a broken dpkg database must be distinguished.
inventory=$(dpkg-query -W -f='${Package} ${db:Status-Status}\n')
if printf '%s\n' "$inventory" | awk '$1 ~ /^daylight-/ && $2 != "not-installed" && $2 != "config-files" {found=1} END {exit !found}'; then
    if [ "$1" = explicit ]; then
        echo 'Daylight packages are still present. Remove them before cleaning the repository.' >&2
        exit 1
    fi
    : > "$state/armed"
    exit 0
fi
if [ "$1" = hook ]; then
    [ -f "$state/armed" ] || exit 0
    case "${DPKG_HOOK_ACTION:-}" in remove|purge) ;; *) exit 0 ;; esac
fi
remove_matching() {
    file=$1
    shift
    [ -e "$file" ] || return 0
    if [ -f "$file" ] && [ ! -L "$file" ]; then
        digest=$(sha256sum "$file")
        for expected do
            if [ "${digest%% *}" = "$expected" ]; then
                rm -- "$file"
                echo "Removed $file"
                return 0
            fi
        done
    fi
    echo "Preserved modified file: $file" >&2
}
remove_matching "$source" afdb6c687f07ad78b86d264749369239e194f104a6e21f45d81186d19003ea3c 5532cb34ba7024a7060e837f3e610f7560c1242480819845acd3a96fea3e39af b5474d0ac43bcf1241060987c6fb871e8d52a5a50693c249c6e2a8f8d58b5c0a f22b2fea5df6f72f57cdaa92e55a08bfd97e0d5b8d78d075a8abb1686d39e5aa
remove_matching "$pin" 60a1e6820ad6d6206b1109f738abed3f22f2fb732b1168b14a304f35798fba59 3ee896e2fba2ddabb25ff045b56619d75405f3d99effb77037731d24bf3909c6
remove_matching "$mirrors" 5e5c8260b35e0cb813ff3ec51055f6625c95b96845129e09ec7d6ee287216486
if [ ! -e "$source" ]; then
    shared=no
    for entry in /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources; do
        [ -f "$entry" ] || continue
        if grep -Fq "$key" "$entry"; then shared=yes; break; fi
    done
    if [ "$shared" = no ]; then remove_matching "$key" f2a244bae188c4f233ad19acdd56f8846486a7d03163c06a29ba644b2d666ef9; fi
fi
if [ -f "$hook" ] && grep -Fxq '# Managed by Daylight GNU/Linux installer' "$hook"; then rm -- "$hook"; fi
if [ -d "$state" ]; then
    rm -f -- "$state/armed" "$state/cleanup"
    rmdir -- "$state"
fi
DAYLIGHT_REPO_CLEANUP
}
if [ "$mode" = remove_repo ]; then
    if [ "$apply" != yes ]; then echo 'Plan: clean the managed Daylight APT files after package removal. Add --yes to apply.'; exit 0; fi
    [ "$(id -u)" -eq 0 ] || { echo 'Run with sudo and --yes.' >&2; exit 2; }
    write_repo_cleanup | sh -s -- explicit
    exit
fi
packages='daylight-core daylight-themes'
if [ "$mode" = desktop ]; then packages='daylight-linux'; fi
if [ "$mode" = repo ]; then packages=''; fi
if [ "$games" = yes ]; then packages="$packages daylight-games"; fi
printf 'Repository: %s\nSigning fingerprint: %s\nArchitecture: %s\nPackages: %s\n' "$BASE" "$FINGERPRINT" "$arch" "${packages:-repository configuration only}"
if [ "$apply" != yes ]; then echo 'Plan only. Add --yes to apply. No file, service or package was changed.'; exit 0; fi
[ "$(id -u)" -eq 0 ] || { echo 'Run the inspected script with sudo and --yes to apply.' >&2; exit 2; }
export DEBIAN_FRONTEND=noninteractive
missing=no
for tool in curl gpg gpgv; do command -v "$tool" >/dev/null 2>&1 || missing=yes; done
if [ "$missing" = yes ]; then
    apt-get -o APT::Update::Error-Mode=any update
    apt-get install --no-remove --no-install-recommends -y ca-certificates curl gnupg gpgv
fi
temporary=$(mktemp -d)
backup=
changed=no
success=no
source=/etc/apt/sources.list.d/daylight.sources
key=/etc/apt/keyrings/daylight-archive-keyring.gpg
pin=/etc/apt/preferences.d/daylight
mirrors=/etc/apt/mirrors/daylight.list
cleanup() {
    code=$?
    if [ "$changed" = yes ] && [ "$success" != yes ]; then
        for name in source key pin mirrors; do
            case "$name" in source) destination=$source ;; key) destination=$key ;; pin) destination=$pin ;; mirrors) destination=$mirrors ;; esac
            if [ -f "$backup/$name" ]; then cp -p "$backup/$name" "$destination"; else rm -f "$destination"; fi
        done
        echo 'Daylight APT configuration restored after failure. Existing package/dependency changes, if any, are not a disk rollback.' >&2
    fi
    rm -rf "$temporary"
    exit "$code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -m 700 "$temporary/gnupg"
fetch() { curl --disable --fail --silent --show-error --location --proto '=https' --proto-redir '=https' --tlsv1.2 --retry 3 --connect-timeout 10 --max-time 90 "$1" -o "$2"; }
fetch "$BASE/daylight-archive-keyring.gpg" "$temporary/key.gpg"
gpg --homedir "$temporary/gnupg" --batch --with-colons --show-keys --fingerprint "$temporary/key.gpg" > "$temporary/key.info"
actual=$(awk -F: '$1=="fpr" {print $10;exit}' "$temporary/key.info")
count=$(awk -F: '$1=="pub" {n++} END {print n+0}' "$temporary/key.info")
[ "$actual" = "$FINGERPRINT" ] && [ "$count" = 1 ] || { echo 'Signing key does not match the pinned fingerprint; nothing installed.' >&2; exit 1; }
fetch "$BASE/dists/daylight/InRelease" "$temporary/InRelease"
gpgv --homedir "$temporary/gnupg" --keyring "$temporary/key.gpg" --output "$temporary/Release" "$temporary/InRelease"
grep -qx 'Origin: Daylight GNU/Linux' "$temporary/Release"
grep -qx 'Codename: daylight' "$temporary/Release"
for destination in "$source" "$key" "$pin" "$mirrors"; do
    [ ! -L "$destination" ] || { echo 'Refusing to replace a symbolic-link configuration.' >&2; exit 1; }
done
for destination in "$source" "$pin" "$mirrors"; do
    if [ -e "$destination" ] && ! grep -q '^# Managed by Daylight GNU/Linux installer$' "$destination"; then
        printf 'Refusing to overwrite existing unmanaged file: %s\n' "$destination" >&2; exit 1
    fi
done
if [ -e "$key" ] && [ ! -e "$source" ]; then echo 'Unmanaged Daylight key already exists; refusing to replace it.' >&2; exit 1; fi
mkdir -p /var/backups /etc/apt/keyrings /etc/apt/sources.list.d /etc/apt/preferences.d /etc/apt/mirrors
backup=$(mktemp -d /var/backups/daylight-apt.XXXXXX)
for name in source key pin mirrors; do
    case "$name" in source) destination=$source ;; key) destination=$key ;; pin) destination=$pin ;; mirrors) destination=$mirrors ;; esac
    if [ -f "$destination" ]; then cp -p "$destination" "$backup/$name"; fi
done
cat > "$temporary/daylight.sources" <<EOF
# Managed by Daylight GNU/Linux installer
Types: deb
URIs: mirror+file:/etc/apt/mirrors/daylight.list
Suites: daylight
Components: main
Architectures: $arch
Signed-By: $key
EOF
cat > "$temporary/preferences" <<'EOF'
# Managed by Daylight GNU/Linux installer
Package: daylight-*
Pin: release o=Daylight GNU/Linux
Pin-Priority: 500

Package: *
Pin: release o=Daylight GNU/Linux
Pin-Priority: -1
EOF
cat > "$temporary/mirrors" <<'EOF'
# Managed by Daylight GNU/Linux installer
https://daylightlinux.ch/apt/	priority=1
https://raw.githubusercontent.com/hamdyaea/Daylight-GNU-Linux/publish/cloudflare-pages-20261103/website-src/apt/	priority=2
https://daylight-gnu-linux.pages.dev/apt/	priority=3
EOF
changed=yes
# Reject empty or malformed mirror files before changing the active APT source.
[ -s "$temporary/mirrors" ] || { echo 'Daylight mirror list is empty.' >&2; exit 1; }
[ "$(grep -Ec '^https://[^[:space:]]+[[:space:]]+priority=[1-3]
install -m 644 "$temporary/key.gpg" "$key"
install -m 644 "$temporary/daylight.sources" "$source"
install -m 644 "$temporary/preferences" "$pin"
# Authentication and expiry checking remain enabled, including all failures.
apt-get -o APT::Update::Error-Mode=any update
desktop_user=
helper=
if [ "$mode" = desktop ]; then
    desktop_user=${SUDO_USER:-}
    if [ -z "$desktop_user" ] || [ "$desktop_user" = root ]; then
        # Only infer the user when exactly one local graphical account is active.
        desktop_user=$(loginctl list-sessions --no-legend 2>/dev/null | while read -r sid rest; do
            case "$(loginctl show-session "$sid" -p Type --value 2>/dev/null)" in
                x11|wayland) loginctl show-session "$sid" -p Name --value ;;
            esac
        done | sort -u | awk 'NR==1 {name=$0} END {if(NR==1) print name}')
    fi
    if [ -n "$desktop_user" ] && [ "$desktop_user" != root ] && [ -r /etc/X11/default-display-manager ]; then
        helper=daylight-session-defaults
        if [ -r /proc/device-tree/model ] && grep -aq 'Raspberry Pi' /proc/device-tree/model; then
            apt-get install --no-remove --no-install-recommends -y $packages "$helper" labwc
        else
            apt-get install --no-remove --no-install-recommends -y $packages "$helper"
        fi
    else
        apt-get install --no-remove --no-install-recommends -y $packages
    fi
elif [ -n "$packages" ]; then
    # Word splitting is deliberate: this is a fixed internal package allowlist.
    apt-get install --no-remove --no-install-recommends -y $packages
fi
state=/var/lib/daylight-apt-lifecycle
hook=/etc/dpkg/dpkg.cfg.d/90-daylight-repository
install -d -m 755 "$state"
write_repo_cleanup > "$temporary/repo-cleanup"
install -m 755 "$temporary/repo-cleanup" "$state/cleanup.new"
mv -f "$state/cleanup.new" "$state/cleanup"
printf '%s\n' '# Managed by Daylight GNU/Linux installer' 'post-invoke=if [ -x /var/lib/daylight-apt-lifecycle/cleanup ]; then /var/lib/daylight-apt-lifecycle/cleanup hook; fi' > "$temporary/dpkg-hook"
install -m 644 "$temporary/dpkg-hook" "$hook"
"$state/cleanup" hook
success=yes
printf 'Daylight installation completed. Configuration backup: %s\n' "$backup"
if [ "$mode" = desktop ]; then
    if [ -n "${helper:-}" ] && /usr/lib/daylight/session-defaults activate "$desktop_user"; then
        printf 'Daylight is selected for %s. The Daylight desktop, wallpaper and system monitor start at graphical login.\n' "$desktop_user"
    else
        echo 'Automatic selection unavailable. Select Daylight GNU/Linux at graphical login.' >&2
    fi
    if [ -t 0 ] && [ -t 1 ] && [ -d /run/systemd/system ]; then
        printf 'Save your work. Reboot now to start the new desktop? [y/N] '
        read -r answer || answer=
        case "$answer" in y|Y|yes|YES|o|O|oui) systemctl reboot ;; esac
    else
        echo 'When ready, reboot with: sudo systemctl reboot'
    fi
fi
 "$temporary/mirrors")" -eq 3 ] || { echo 'Daylight mirror list is incomplete.' >&2; exit 1; }
install -m 644 "$temporary/mirrors" "$mirrors"
[ -s "$mirrors" ] || { echo 'Daylight mirror installation failed.' >&2; exit 1; }
install -m 644 "$temporary/key.gpg" "$key"
install -m 644 "$temporary/daylight.sources" "$source"
install -m 644 "$temporary/preferences" "$pin"
# Authentication and expiry checking remain enabled, including all failures.
apt-get -o APT::Update::Error-Mode=any update
desktop_user=
helper=
if [ "$mode" = desktop ]; then
    desktop_user=${SUDO_USER:-}
    if [ -z "$desktop_user" ] || [ "$desktop_user" = root ]; then
        # Only infer the user when exactly one local graphical account is active.
        desktop_user=$(loginctl list-sessions --no-legend 2>/dev/null | while read -r sid rest; do
            case "$(loginctl show-session "$sid" -p Type --value 2>/dev/null)" in
                x11|wayland) loginctl show-session "$sid" -p Name --value ;;
            esac
        done | sort -u | awk 'NR==1 {name=$0} END {if(NR==1) print name}')
    fi
    if [ -n "$desktop_user" ] && [ "$desktop_user" != root ] && [ -r /etc/X11/default-display-manager ]; then
        helper=daylight-session-defaults
        if [ -r /proc/device-tree/model ] && grep -aq 'Raspberry Pi' /proc/device-tree/model; then
            apt-get install --no-remove --no-install-recommends -y $packages "$helper" labwc
        else
            apt-get install --no-remove --no-install-recommends -y $packages "$helper"
        fi
    else
        apt-get install --no-remove --no-install-recommends -y $packages
    fi
elif [ -n "$packages" ]; then
    # Word splitting is deliberate: this is a fixed internal package allowlist.
    apt-get install --no-remove --no-install-recommends -y $packages
fi
state=/var/lib/daylight-apt-lifecycle
hook=/etc/dpkg/dpkg.cfg.d/90-daylight-repository
install -d -m 755 "$state"
write_repo_cleanup > "$temporary/repo-cleanup"
install -m 755 "$temporary/repo-cleanup" "$state/cleanup.new"
mv -f "$state/cleanup.new" "$state/cleanup"
printf '%s\n' '# Managed by Daylight GNU/Linux installer' 'post-invoke=if [ -x /var/lib/daylight-apt-lifecycle/cleanup ]; then /var/lib/daylight-apt-lifecycle/cleanup hook; fi' > "$temporary/dpkg-hook"
install -m 644 "$temporary/dpkg-hook" "$hook"
"$state/cleanup" hook
success=yes
printf 'Daylight installation completed. Configuration backup: %s\n' "$backup"
if [ "$mode" = desktop ]; then
    if [ -n "${helper:-}" ] && /usr/lib/daylight/session-defaults activate "$desktop_user"; then
        printf 'Daylight is selected for %s. The Daylight desktop, wallpaper and system monitor start at graphical login.\n' "$desktop_user"
    else
        echo 'Automatic selection unavailable. Select Daylight GNU/Linux at graphical login.' >&2
    fi
    if [ -t 0 ] && [ -t 1 ] && [ -d /run/systemd/system ]; then
        printf 'Save your work. Reboot now to start the new desktop? [y/N] '
        read -r answer || answer=
        case "$answer" in y|Y|yes|YES|o|O|oui) systemctl reboot ;; esac
    else
        echo 'When ready, reboot with: sudo systemctl reboot'
    fi
fi
