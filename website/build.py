#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Build the bilingual, tracker-free static Daylight website from release metadata."""
import argparse
import hashlib
from html import escape as e
import json
from pathlib import Path
import shutil
import zipfile
from PIL import Image
from discovery import enhance

ROOT = Path(__file__).resolve().parent.parent
GITHUB = 'https://github.com/hamdyaea/Daylight-GNU-Linux'
BOOKS = 'https://www.amazon.fr/stores/author/B0BM89T88X'
CONTACT = 'info@daylightlinux.ch'
FPR = 'B0575F821A31DD20753DE07C50D21240F4BCB02E'
COPY = {
 'en': {
  'nav': ['Download', 'Install', 'Try online', 'Wallpapers', 'Books', 'Old'],
  'hero': 'Less overhead.<br><em>More daylight.</em>',
  'intro': 'A lightweight Linux desktop with a Rust toolkit, a familiar Debian foundation and room to make it your own.',
  'get': 'Get Daylight', 'try': 'Try in your browser', 'candidate': 'Release candidate',
  'sub': 'For 64-bit PCs and Raspberry Pi systems. Free software, built in Switzerland.',
  'small': 'No background tracking. No forced desktop replacement. No oversized web-based toolkit.',
  'philosophy': 'A quieter kind of desktop.',
  'philosophy_text': 'Fluxbox keeps the essentials close. Conky puts system information in view. Small Rust utilities do useful work without a permanent application server.',
  'cards': [('01 / DESKTOP','Light by design','An independent Fluxbox session, a configurable system monitor and a terminal that starts without external network requests.'),('02 / TOOLKIT','Small tools. Real work.','Passwords, temperature conversion, dates, local network information, timers and offline games including Shardturn. Illustrated native windows open on demand.'),('03 / CONTROL','Your machine, your choice.','Install just the command-line core, or add the desktop. Existing shell and desktop files stay separate. Telemetry stays off.')],
  'install_title': 'A familiar way to install.', 'install_intro': 'Debian packages from a signed APT repository, architecture detection and an installer that shows its plan before changing anything.',
  'install_link': 'Read the installation guide', 'art_title': 'A desktop with a view.',
  'art_text': 'A photorealistic Alpine lake, golden mountain photographs and a darker variant. Every landscape carries the Daylight Linux signature. No image downloads at login.',
  'art_link': 'Explore the wallpapers', 'download_title': 'Choose your Daylight.',
  'download_intro': 'Use the PC live image to explore, or install the matching packages on an existing Debian-based system.',
  'pc': 'PC live image', 'pc_text': 'Debian 13 live environment for AMD64 PCs. Temporary by default, with no disk installer or persistence. This is not a Raspberry Pi boot image.',
  'iso_button': 'Download the AMD64 ISO', 'pi': 'Debian & Raspberry Pi OS', 'pi_text': 'ARM64 and AMD64 packages for existing 64-bit systems. Start with the core on a server; choose the desktop only when you need it.',
  'packages_button': 'Install with APT', 'all_assets': 'All release files & checksums',
  'install_page': 'Install without taking over.', 'install_lead': 'The default plan is core-only. Use --all to add the desktop, games and optional telemetry package; telemetry remains disabled until explicit opt-in.',
  'step1': '1. Download and inspect', 'step1text': 'Download the script as a file, inspect it, then print its plan. The script is not piped into a privileged shell.',
  'step2': '2. Choose the scope', 'step2text': 'Core-only adds command-line tools and backgrounds. Desktop adds Fluxbox and applications. --all also includes games and the optional telemetry package; telemetry remains disabled. No mode starts or replaces a display manager.',
  'desktop_label': 'Desktop:', 'desktop_games_label': 'Desktop + games:', 'all_install_label': 'Full installation:', 'all_install_note': 'The telemetry package stays off. It sends no event until you explicitly run sudo daylight telemetry on.',
  'step3': '3. Keep it current', 'step3text': 'APT verifies signed metadata and package hashes. Daylight updates request only installed Daylight packages, not a distribution upgrade.',
  'remove': 'Remove Daylight', 'remove_text': 'Log out of the Daylight desktop before removing it. Removal does not run autoremove; shared dependencies and personal settings are retained.',
  'trust': 'Repository trust', 'trust_text': 'The installer checks this complete signing-key fingerprint before accepting the repository. Its APT pinning excludes non-Daylight packages from this origin. No trusted=yes or unauthenticated installation is used.',
  'compat': 'Compatibility', 'compat_text': 'Target systems: Debian 12/13 and compatible 64-bit Raspberry Pi OS. ARM32 and Arch/Manjaro are not supported by the installer. APT may install required dependencies; this is not a snapshot rollback.',
  'try_title': 'A real Linux session.<br>Inside your browser.', 'try_lead': 'Explore the actual AMD64 live image through QEMU and noVNC in your own disposable development environment, without booting your computer from USB.',
  'codespace': 'Private browser demo', 'codespace_text': 'The repository includes a ready-to-launch Codespaces configuration. Sign in to GitHub, create the environment and open the forwarded Daylight port. The guest has no network adapter, no host disk and no persistence.',
  'codespace_button': 'Open the demo configuration', 'billing': 'Codespaces uses your own GitHub compute and storage allowance. Charges can apply beyond your quota. Stopping the demo is not the same as deleting the Codespace.',
  'local_demo': 'Run it locally', 'local_demo_text': 'The same noVNC demo can run in a resource-limited container on your own test computer. It listens only on localhost by default. Do not expose an unauthenticated shared VM to the internet.',
  'distrosea': 'About DistroSea', 'distrosea_text': 'DistroSea offers hosted Linux trials. Daylight is not currently listed; inclusion is controlled by its operator. There is no self-service upload or guaranteed acceptance advertised on its contact page.',
  'v86': 'Why not load the 64-bit ISO directly in WebAssembly?', 'v86_text': 'v86 does not support 64-bit kernels. A browser-only 32-bit port would be a different edition, not a test of this AMD64 ISO. The supplied QEMU/noVNC route runs the actual release image.',
  'walls': 'Bring the outside in.', 'walls_intro': 'Golden light. Mountain horizons. The Daylight Linux signature. The approved generated landscape is 1672 × 941; the two real photographs are rendered at native 4K.',
  'wall_names': ['Alpine lake at dawn','Sun above the clouds','Alpine lake — dusk palette','Himalayan dawn'],
  'wall_note': 'The Alpine lake is AI-generated scenery, not an identified real location. Its dark variant adjusts exposure. The other two landscapes are real CC0 photographs. Credits, source checksums and exact resolutions are documented.',
  'old_title': 'Earlier chapters.', 'old_intro': 'Historical releases stay available here. They are archived for reference, not recommended for exposed or security-sensitive systems.',
  'old_site': 'Visit the previous website', 'old_sources': 'Browse the preserved source branches',
  'privacy': 'Privacy, plainly.', 'privacy_text': 'Daylight works locally by default. Opening its terminal does not make an external request. The optional boot counter is a separate package, off until explicitly enabled. It counts received boot events, not unique users. No production collector is activated by the installer.',
  'web_privacy': 'This static website includes no analytics scripts, advertising trackers or external fonts. Hosting and network providers can see connection metadata and may use security cookies; this is not a promise of anonymous transport.',
  'credits': 'Photographic credits', 'verified': 'Inspect the validation evidence', 'footer': 'Created by Hamdy Abou El Anein. Daylight code: GNU GPL v3. Artwork credits are provided separately.',
  'skip': 'Skip to content', 'copy': 'Copy command', 'more': 'Documentation & source', 'live_caption': 'Real live-session screenshot from the published candidate.'
 },
 'fr': {
  'nav': ['Télécharger', 'Installer', 'Essayer', 'Fonds d’écran', 'Livres', 'Old'],
  'hero': 'Moins de superflu.<br><em>Plus de Daylight.</em>',
  'intro': 'Un bureau Linux léger, des outils en Rust, une base Debian familière et la liberté de le personnaliser.',
  'get': 'Télécharger Daylight', 'try': 'Essayer dans le navigateur', 'candidate': 'Version candidate',
  'sub': 'Pour PC 64 bits et systèmes Raspberry Pi. Un logiciel libre développé en Suisse.',
  'small': 'Pas de suivi en arrière-plan. Pas de remplacement imposé du bureau. Pas de lourde interface web pour les outils.',
  'philosophy': 'Un bureau qui va à l’essentiel.',
  'philosophy_text': 'Fluxbox garde vos outils à portée de main. Conky affiche les informations système. De petits utilitaires Rust font leur travail sans serveur applicatif permanent.',
  'cards': [('01 / BUREAU','Léger par conception','Une session Fluxbox indépendante, un moniteur configurable et un terminal qui démarre sans requête réseau externe.'),('02 / OUTILS','Petits outils. Vrais usages.','Mots de passe, températures, dates, réseau local, minuterie et jeux hors ligne, dont Shardturn. Les fenêtres natives illustrées s’ouvrent à la demande.'),('03 / LIBERTÉ','Votre machine, votre choix.','Installez uniquement les outils CLI ou ajoutez le bureau. Vos réglages existants restent séparés. La télémétrie reste désactivée.')],
  'install_title': 'Une installation familière.', 'install_intro': 'Un dépôt APT signé, la détection de l’architecture et un script qui affiche son plan avant toute modification.',
  'install_link': 'Lire le guide d’installation', 'art_title': 'Un bureau ouvert sur la nature.',
  'art_text': 'Un lac alpin photoréaliste, des photographies de sommets dorés et une variante assombrie. Chaque paysage porte la signature Daylight Linux. Aucun téléchargement à l’ouverture de session.',
  'art_link': 'Découvrir les fonds d’écran', 'download_title': 'Choisissez votre Daylight.',
  'download_intro': 'Explorez l’image live pour PC ou installez les paquets adaptés sur votre système Debian existant.',
  'pc': 'Image live pour PC', 'pc_text': 'Environnement live Debian 13 pour PC AMD64. Temporaire par défaut, sans installateur disque ni persistance. Ce n’est pas une image de démarrage pour Raspberry Pi.',
  'iso_button': 'Télécharger l’ISO AMD64', 'pi': 'Debian et Raspberry Pi OS', 'pi_text': 'Paquets ARM64 et AMD64 pour systèmes 64 bits existants. Commencez par le cœur CLI sur un serveur ; ajoutez le bureau uniquement si nécessaire.',
  'packages_button': 'Installer avec APT', 'all_assets': 'Tous les fichiers et sommes de contrôle',
  'install_page': 'Installer sans tout remplacer.', 'install_lead': 'Le plan par défaut concerne uniquement le cœur. --all ajoute le bureau, les jeux et le paquet optionnel de télémétrie, qui reste désactivée jusqu’à votre accord explicite.',
  'step1': '1. Télécharger et vérifier', 'step1text': 'Téléchargez le script, lisez-le, puis affichez son plan. Il n’est pas envoyé directement dans un shell privilégié.',
  'step2': '2. Choisir le périmètre', 'step2text': 'Le mode core ajoute les outils CLI et les fonds d’écran. Le mode desktop ajoute Fluxbox et les applications. --all inclut aussi les jeux et le paquet optionnel de télémétrie, qui reste désactivée. Aucun mode ne démarre ni ne remplace le gestionnaire de connexion.',
  'desktop_label': 'Bureau :', 'desktop_games_label': 'Bureau + jeux :', 'all_install_label': 'Installation complète :', 'all_install_note': 'Le paquet de télémétrie reste désactivé. Aucun événement n’est envoyé avant l’activation explicite avec sudo daylight telemetry on.',
  'step3': '3. Garder Daylight à jour', 'step3text': 'APT vérifie les métadonnées signées et l’intégrité des paquets. La commande Daylight cible les paquets Daylight installés, pas une mise à niveau de la distribution.',
  'remove': 'Supprimer Daylight', 'remove_text': 'Quittez la session graphique Daylight avant la suppression. Aucun autoremove n’est exécuté ; les dépendances partagées et vos réglages personnels sont conservés.',
  'trust': 'Confiance dans le dépôt', 'trust_text': 'Le script vérifie cette empreinte complète avant d’accepter le dépôt. Les priorités APT excluent les paquets non-Daylight de cette origine. Aucun trusted=yes ni contournement des signatures.',
  'compat': 'Compatibilité', 'compat_text': 'Systèmes ciblés : Debian 12/13 et Raspberry Pi OS 64 bits compatible. ARM32 et Arch/Manjaro ne sont pas pris en charge par le script. APT peut installer des dépendances ; la désinstallation n’est pas une restauration de snapshot.',
  'try_title': 'Une vraie session Linux.<br>Dans votre navigateur.', 'try_lead': 'Explorez la véritable image live AMD64 avec QEMU et noVNC dans votre environnement de développement jetable, sans démarrer votre PC sur une clé USB.',
  'codespace': 'Démonstration privée', 'codespace_text': 'Le dépôt contient une configuration Codespaces prête à lancer. Connectez-vous à GitHub, créez l’environnement puis ouvrez le port Daylight redirigé. La machine invitée n’a ni carte réseau, ni disque hôte, ni persistance.',
  'codespace_button': 'Ouvrir la configuration de démonstration', 'billing': 'Codespaces utilise votre quota de calcul et de stockage GitHub. Des frais sont possibles au-delà. Arrêter la démonstration ne supprime pas le Codespace.',
  'local_demo': 'Essayer localement', 'local_demo_text': 'La même démonstration noVNC fonctionne dans un conteneur limité en ressources sur votre machine de test. Elle écoute uniquement sur localhost par défaut. N’exposez pas de VM partagée sans authentification sur Internet.',
  'distrosea': 'À propos de DistroSea', 'distrosea_text': 'DistroSea propose des essais Linux hébergés. Daylight n’y figure pas actuellement ; son ajout dépend de l’exploitant. Sa page de contact ne propose ni dépôt libre d’ISO ni acceptation garantie.',
  'v86': 'Pourquoi ne pas charger cette ISO 64 bits directement en WebAssembly ?', 'v86_text': 'v86 ne prend pas en charge les noyaux 64 bits. Un portage 32 bits pour navigateur serait une autre édition, pas un essai de cette ISO AMD64. La solution QEMU/noVNC fournie utilise la véritable image publiée.',
  'walls': 'La nature, sans filtre graphique.', 'walls_intro': 'Lumière dorée, horizons de montagne et signature Daylight Linux. Le paysage généré approuvé mesure 1672 × 941 ; les deux véritables photographies sont proposées en 4K native.',
  'wall_names': ['Lac alpin à l’aube','Soleil au-dessus des nuages','Lac alpin — palette sombre','Aube himalayenne'],
  'wall_note': 'Le lac alpin est un paysage généré par IA, pas un lieu réel identifié. Sa variante sombre adapte l’exposition. Les deux autres paysages sont de véritables photographies CC0. Crédits, empreintes et résolutions exactes sont documentés.',
  'old_title': 'Les chapitres précédents.', 'old_intro': 'Les versions historiques restent accessibles ici. Conservées pour référence, elles ne sont pas recommandées pour des systèmes exposés ou sensibles.',
  'old_site': 'Visiter l’ancien site', 'old_sources': 'Consulter les branches archivées',
  'privacy': 'La confidentialité, clairement.', 'privacy_text': 'Daylight fonctionne localement par défaut. Son terminal n’effectue aucune requête externe à l’ouverture. Le compteur de démarrages est un paquet séparé, désactivé jusqu’à votre choix explicite. Il compte des événements reçus, pas des utilisateurs uniques. Le script n’active aucun collecteur de production.',
  'web_privacy': 'Ce site statique ne contient aucun script analytique, traqueur publicitaire ou police externe. Les prestataires d’hébergement et de réseau peuvent voir les métadonnées de connexion et utiliser des cookies de sécurité : le transport n’est pas présenté comme anonyme.',
  'credits': 'Crédits photographiques', 'verified': 'Consulter les preuves de validation', 'footer': 'Créé par Hamdy Abou El Anein. Code Daylight : GNU GPL v3. Crédits des images disponibles séparément.',
  'skip': 'Aller au contenu', 'copy': 'Copier la commande', 'more': 'Documentation et sources', 'live_caption': 'Capture réelle de la session live de la version candidate publiée.'
 }
}


def build(out, evidence=None):
    release = json.loads((ROOT / 'release/current.json').read_text())
    version = release['version']
    release_url = GITHUB + '/releases/tag/' + release['tag']
    download_url = GITHUB + '/releases/download/' + release['tag'] + '/' + release['iso']
    out.mkdir(parents=True, exist_ok=True)
    def write(name, text):
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    def copy(source, destination):
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name in ('style.css', 'main.js'):
        copy(ROOT / 'website' / name, 'assets/v5/' + name)
    copy(ROOT / 'assets/branding/daylight.svg', 'assets/v5/daylight.svg')
    copy(ROOT / 'scripts/install-daylight.sh', 'install.sh')
    copy(ROOT / 'assets/wallpapers/CREDITS.txt', 'media/CREDITS.txt')
    for name in ('daylight-mountains', 'daylight-sunrise', 'daylight-night', 'daylight-himalaya'):
        source = ROOT / 'assets/wallpapers' / (name + '.jpg')
        copy(source, 'media/wallpapers/' + source.name)
        with Image.open(source) as im:
            for width in (720, 1600):
                preview = im.copy()
                preview.thumbnail((width, width), Image.Resampling.LANCZOS)
                preview.save(out / 'media' / (name + '-' + str(width) + '.webp'), quality=80, method=6)
    for item in json.loads((ROOT / 'assets/photography.json').read_text()):
        copy(ROOT / 'dist/photography-source' / (item['name'] + '.jpg'), 'media/source/' + item['name'] + '.jpg')
    screenshot = None
    if evidence:
        candidate = evidence / 'live-test/desktop.png'
        if candidate.is_file():
            copy(candidate, 'media/live-desktop.png')
            screenshot = '/media/live-desktop.png'
    with zipfile.ZipFile(out / 'media/daylight-wallpapers.zip', 'w', zipfile.ZIP_STORED) as archive:
        for p in sorted((out / 'media/wallpapers').glob('*.jpg')):
            archive.write(p, p.name)
        archive.write(out / 'media/CREDITS.txt', 'CREDITS.txt')
    codespaces = 'https://github.com/codespaces/new?hide_repo_select=true&repo=90353020&ref=master&devcontainer_path=.devcontainer%2Fdemo%2Fdevcontainer.json'
    pages = ['index.html', 'download.html', 'install.html', 'try-online.html', 'wallpapers.html', 'books.html', 'old/index.html', 'privacy.html']
    urls = []
    for lang, t in COPY.items():
        prefix = '/fr/' if lang == 'fr' else '/'
        def link(name): return prefix + name
        def button(url, label, secondary=False):
            return '<a class="button' + (' secondary' if secondary else '') + '" href="' + e(url, quote=True) + '">' + e(label) + ' <span aria-hidden="true">↗</span></a>'
        def code(text):
            return '<div class="codebox"><pre><code>' + e(text) + '</code></pre><button type="button" data-copy>' + e(t['copy']) + '</button></div>'
        for page in pages:
            nav_names = pages[1:7]
            nav = ''.join('<a href="' + link(p) + '"' + (' aria-current="page"' if p == page else '') + '>' + e(label) + '</a>' for p, label in zip(nav_names, t['nav']))
            other = ('/' if lang == 'fr' else '/fr/') + page
            nav += '<a class="lang" lang="' + ('en' if lang == 'fr' else 'fr') + '" hreflang="' + ('en' if lang == 'fr' else 'fr') + '" href="' + other + '">' + ('EN' if lang == 'fr' else 'FR') + '</a>'
            head_title = {'index.html':'Daylight GNU/Linux','download.html':t['download_title'],'install.html':t['install_page'],'try-online.html':t['codespace'],'wallpapers.html':t['walls'],'books.html':('Books' if lang == 'en' else 'Livres'),'old/index.html':t['old_title'],'privacy.html':t['privacy']}[page]
            def pagehead(title, lead):
                return '<section class="pagehead"><div class="wrap"><p class="eyebrow">DAYLIGHT GNU/LINUX / ' + e(version) + '</p><h1>' + title + '</h1><p class="lead">' + e(lead) + '</p></div></section>'
            body = ''
            if page == 'index.html':
                body = '<section class="hero"><div class="wrap"><p class="pill"><span class="dot"></span>' + e(t['candidate'] + ' ' + version) + '</p><h1>' + t['hero'] + '</h1><p class="lead">' + e(t['intro']) + '</p><div class="actions">' + button(link('download.html'),t['get']) + button(link('try-online.html'),t['try'],True) + '</div><p class="small">' + e(t['sub']) + '</p></div></section>'
                body += '<div class="wrap"><div class="strip">' + ''.join('<div><strong>' + a + '</strong><span>' + b + '</span></div>' for a,b in [('Debian','12 / 13'),('Fluxbox','Desktop'),('Rust','Core toolkit'),('AMD64 + ARM64','64-bit')]) + '</div></div>'
                body += '<section class="section"><div class="wrap"><p class="eyebrow">THE DAYLIGHT WAY</p><h2>' + e(t['philosophy']) + '</h2><p class="lead">' + e(t['philosophy_text']) + '</p><div class="grid">'
                for index,title,text in t['cards']:
                    body += '<article class="card"><span class="index">' + e(index) + '</span><h3>' + e(title) + '</h3><p>' + e(text) + '</p></article>'
                body += '</div></div></section>'
                body += '<section class="section tight"><div class="wrap split"><div><p class="eyebrow">APT / DEBIAN</p><h2>' + e(t['install_title']) + '</h2><p class="lead">' + e(t['install_intro']) + '</p>' + button(link('install.html'),t['install_link'],True) + '</div><div>' + code('curl -fsSLo install-daylight.sh https://daylightlinux.ch/install.sh\nsh install-daylight.sh --plan') + '<p class="small">' + e(t['small']) + '</p></div></div></section>'
                body += '<section class="section tight"><div class="wrap split"><figure class="art"><img src="/media/daylight-sunrise-720.webp" alt="Mountain sunrise above clouds" loading="lazy" width="720" height="405"><figcaption>Alice Donovan Rouse · CC0</figcaption></figure><div><p class="eyebrow">DAYLIGHT / LANDSCAPES</p><h2>' + e(t['art_title']) + '</h2><p class="lead">' + e(t['art_text']) + '</p>' + button(link('wallpapers.html'),t['art_link'],True) + '</div></div></section>'
                if screenshot:
                    body += '<section class="section tight"><div class="wrap"><figure><img class="screenshot" src="' + screenshot + '" alt="Daylight Fluxbox live desktop" loading="lazy"><figcaption class="small">' + e(t['live_caption']) + '</figcaption></figure></div></section>'
                body += '<section class="section tight"><div class="wrap"><div class="cta"><h2>' + e(t['get']) + '</h2><p class="lead">' + e(t['sub']) + '</p><div class="actions">' + button(link('download.html'),t['get']) + button(GITHUB,t['more'],True) + '</div></div></div></section>'
            elif page == 'download.html':
                body = pagehead(e(t['download_title']),t['download_intro']) + '<section class="section"><div class="wrap grid two"><article class="card"><span class="tag">AMD64 / LIVE ISO</span><h2>' + e(t['pc']) + '</h2><p>' + e(t['pc_text']) + '</p><p class="small">' + e(version) + ' · ' + f'{release["iso_bytes"]/1e9:.2f} GB' + '</p>' + button(download_url,t['iso_button']) + '<p class="small note">SHA-256</p><p class="checksum">' + e(release['iso_sha256']) + '</p></article><article class="card"><span class="tag">ARM64 + AMD64 / APT</span><h2>' + e(t['pi']) + '</h2><p>' + e(t['pi_text']) + '</p>' + button(link('install.html'),t['packages_button']) + '<p class="note"><a href="' + release_url + '">' + e(t['all_assets']) + '</a></p><p><a href="' + GITHUB + '/actions/runs/' + str(release['validation_run']) + '">' + e(t['verified']) + '</a></p></article></div></section>'
            elif page == 'install.html':
                body = pagehead(e(t['install_page']),t['install_lead']) + '<section class="section"><div class="wrap prose"><h2 id="step1">' + e(t['step1']) + '</h2><p>' + e(t['step1text']) + '</p>' + code('curl -fsSLo install-daylight.sh https://daylightlinux.ch/install.sh\nless install-daylight.sh\nsh install-daylight.sh --core --plan')
                body += '<h2 id="step2">' + e(t['step2']) + '</h2><p>' + e(t['step2text']) + '</p>' + code('sudo sh install-daylight.sh --core --yes') + '<h3 id="desktop">' + e(t['desktop_label']) + '</h3>' + code('sudo sh install-daylight.sh --desktop --yes') + '<h3 id="games">' + e(t['desktop_games_label']) + '</h3>' + code('sudo sh install-daylight.sh --desktop --games --yes') + '<h3 id="all">' + e(t['all_install_label']) + '</h3>' + code('sudo sh install-daylight.sh --all --yes') + '<p class="small note">' + e(t['all_install_note']) + '</p>'
                body += '<h2>' + e(t['trust']) + '</h2><p>' + e(t['trust_text']) + '</p><div class="callout checksum">' + FPR + '</div><p><a href="/apt/daylight-archive-keyring.gpg">Public archive key</a> · <a href="/apt/dists/daylight/InRelease">InRelease</a> · <a href="/apt/status.json">Archive status</a></p>'
                body += '<h2 id="step3">' + e(t['step3']) + '</h2><p>' + e(t['step3text']) + '</p>' + code('daylight update --dry-run\nsudo daylight update') + '<h2>' + e(t['remove']) + '</h2><p>' + e(t['remove_text']) + '</p>' + code('daylight remove --dry-run\nsudo daylight remove') + '<h2>' + e(t['compat']) + '</h2><p>' + e(t['compat_text']) + '</p></div></section>'
            elif page == 'try-online.html':
                body = pagehead(t['try_title'],t['try_lead']) + '<section class="section"><div class="wrap"><div class="grid two"><article class="card"><span class="tag">QEMU + NOVNC</span><h2>' + e(t['codespace']) + '</h2><p>' + e(t['codespace_text']) + '</p>' + button(codespaces,t['codespace_button']) + '<p class="small note">' + e(t['billing']) + '</p></article><article class="card"><span class="tag">LOCALHOST / CONTAINER</span><h2>' + e(t['local_demo']) + '</h2><p>' + e(t['local_demo_text']) + '</p><a class="textlink" href="' + GITHUB + '/blob/master/demo/README.md">' + e(t['more']) + ' ↗</a></article></div><div class="prose"><h2>' + e(t['distrosea']) + '</h2><p>' + e(t['distrosea_text']) + '</p><a href="https://distrosea.com/">DistroSea ↗</a><h2>' + e(t['v86']) + '</h2><p>' + e(t['v86_text']) + '</p></div></div></section>'
            elif page == 'wallpapers.html':
                body = pagehead(e(t['walls']),t['walls_intro']) + '<section class="section"><div class="wrap"><div class="grid gallery">'
                for name,title,author in zip(('daylight-mountains','daylight-sunrise','daylight-night','daylight-himalaya'),t['wall_names'],('Daylight · AI-generated','Alice Donovan Rouse · CC0','Daylight · AI-generated derivative','Ali Sabbagh · CC0')):
                    body += '<article class="card"><img src="/media/' + name + '-720.webp" alt="' + e(title,quote=True) + '" width="720" height="405" loading="lazy"><div class="pad"><h3>' + e(title) + '</h3><p>' + author + '</p>' + button('/media/wallpapers/' + name + '.jpg',('3840 × 2160 JPG' if name in ('daylight-sunrise','daylight-himalaya') else '1672 × 941 JPG'),True) + '</div></article>'
                body += '</div><div class="callout">' + e(t['wall_note']) + '</div><div class="actions">' + button('/media/daylight-wallpapers.zip','Wallpapers ZIP') + button('/media/CREDITS.txt',t['credits'],True) + '</div></div></section>'
            elif page == 'books.html':
                title = 'Read. Learn. Build.' if lang == 'en' else 'Lire. Apprendre. Construire.'
                lead = ('Books by Hamdy Abou El Anein, founder and developer of Daylight GNU/Linux.' if lang == 'en' else 'Les livres de Hamdy Abou El Anein, fondateur et développeur de Daylight GNU/Linux.')
                label = 'Explore my books on Amazon' if lang == 'en' else 'Découvrir mes livres sur Amazon'
                note = ('Browse the author page for the available titles, editions and current prices. You will leave the Daylight website; Amazon applies its own privacy and purchasing terms.' if lang == 'en' else 'La page auteur présente les titres disponibles, leurs éditions et les prix actuels. Vous quittez le site Daylight ; les règles de confidentialité et de vente d’Amazon s’appliquent.')
                body = pagehead(title, lead) + '<section class="section"><div class="wrap split"><div class="book-art" aria-hidden="true"><span>HAMDY ABOU EL ANEIN</span><strong>Read.<br>Learn.<br>Build.</strong><i>Linux · Technology · Knowledge</i></div><article class="prose"><p class="eyebrow">HAMDY ABOU EL ANEIN</p><h2>' + ('From practice to the page.' if lang == 'en' else 'De la pratique aux livres.') + '</h2><p class="lead">' + e(lead) + '</p><div class="actions">' + button(BOOKS, label) + '</div><p class="small note">' + e(note) + '</p><p><a href="mailto:' + CONTACT + '">' + CONTACT + '</a></p></article></div></section>'
            elif page == 'old/index.html':
                body = pagehead(e(t['old_title']),t['old_intro']) + '<section class="section"><div class="wrap"><div class="grid"><article class="card"><span class="tag">2019 / RASPBERRY PI</span><h3>Daylight Linux 4</h3><a href="https://sourceforge.net/projects/daylight-linux/files/Daylight-GNU-Linux-RPI-Version4/">SourceForge ↗</a></article><article class="card"><span class="tag">2019 / AMD64</span><h3>Daylight Linux 4.01</h3><a href="https://sourceforge.net/projects/daylight-linux/files/Daylight_Linux_amd64_Version4.01/">SourceForge ↗</a></article><article class="card"><span class="tag">ARCHIVE</span><h3>Versions 1–4</h3><a href="https://sourceforge.net/projects/daylight-linux/files/">SourceForge ↗</a></article></div><div class="actions">' + button('/old/site/index.html',t['old_site'],True) + button(GITHUB + '/branches',t['old_sources'],True) + '</div><p class="small note"><a href="' + GITHUB + '/releases/tag/v5.0.0-rc.1">Daylight GNU/Linux 5.0.0-rc.1</a></p></div></section>'
            else:
                body = pagehead(e(t['privacy']),t['privacy_text']) + '<section class="section"><div class="wrap prose"><h2>Website</h2><p>' + e(t['web_privacy']) + '</p><h2>' + e(t['credits']) + '</h2><p><a href="/media/CREDITS.txt">Artwork provenance, licenses and checksums</a></p><h2>GNU GPL v3</h2><p><a href="' + GITHUB + '/blob/master/LICENSE">Daylight source license</a> · <a href="' + GITHUB + '/blob/master/docs/THIRD_PARTY.md">Third-party notices</a></p><h2>Contact</h2><p><a href="mailto:' + CONTACT + '">' + CONTACT + '</a> · <a href="' + GITHUB + '/issues">GitHub Issues</a></p></div></section>'
            canonical = 'https://daylightlinux.ch' + prefix + ('' if page == 'index.html' else page)
            document = '<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="' + e(t['intro'],quote=True) + '"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src &#39;self&#39;; img-src &#39;self&#39; data:; style-src &#39;self&#39;; script-src &#39;self&#39;; connect-src &#39;self&#39;; object-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;; frame-src &#39;none&#39;"><title>' + e(head_title) + ' — Daylight GNU/Linux</title><link rel="canonical" href="' + canonical + '"><link rel="alternate" hreflang="en" href="https://daylightlinux.ch/' + page + '"><link rel="alternate" hreflang="fr" href="https://daylightlinux.ch/fr/' + page + '"><link rel="icon" href="/assets/v5/daylight.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/v5/style.css"><script src="/assets/v5/main.js" defer></script></head><body><a class="skip" href="#main">' + e(t['skip']) + '</a><header class="header"><div class="wrap"><div class="nav"><a class="brand" href="' + link('index.html') + '"><img src="/assets/v5/daylight.svg" alt="" width="42" height="42"><span>Daylight</span><span>GNU/LINUX</span></a><nav class="links" aria-label="Main">' + nav + '</nav></div></div></header><main id="main">' + body + '</main><div class="wrap"><p class="status" id="copy-status" aria-live="polite"></p></div><footer class="footer"><div class="wrap footgrid"><div><a class="brand" href="' + link('index.html') + '">Daylight GNU/Linux</a><p>' + e(t['footer']) + '</p></div><div class="footlinks"><a href="' + link('privacy.html') + '">' + e(t['privacy']) + '</a><a href="' + GITHUB + '">GitHub</a><a href="' + link('books.html') + '">' + ('Books' if lang == 'en' else 'Livres') + '</a><a href="mailto:' + CONTACT + '">' + CONTACT + '</a><a href="' + link('old/index.html') + '">Old</a></div></div></footer></body></html>'
            filename = ('fr/' if lang == 'fr' else '') + page
            write(filename, document)
            urls.append(canonical)
    # Keep historical inbound URLs useful without server rewrite changes.
    for old,new in [('information.html','install.html'),('screenshots.html','wallpapers.html'),('news.html','download.html'),('linux-book.html','books.html'),('merchandise.html','old/site/merchandise.html')]:
        write(old, '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=/' + new + '"><title>Daylight GNU/Linux</title><p><a href="/' + new + '">Continue to Daylight GNU/Linux</a></p></html>')
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: https://daylightlinux.ch/sitemap.xml\n')
    urls.extend(["https://daylightlinux.ch/mirrors.html", "https://daylightlinux.ch/fr/mirrors.html"])
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + e(url) + '</loc></url>' for url in urls) + '</urlset>')
    enhance(out, release, evidence)
    copy(ROOT / "website-src/mirrors.html", "mirrors.html")
    copy(ROOT / "website-src/fr/mirrors.html", "fr/mirrors.html")
    manifest = {str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'site-manifest.json' and p.relative_to(out).parts[0] != 'live'}
    write('site-manifest.json',json.dumps({'release':release,'files':manifest},indent=2)+'\n')
    print('Bilingual static site built:',out,'files:',len(manifest))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'dist/site')
    parser.add_argument('--evidence',type=Path)
    args=parser.parse_args()
    build(args.output.resolve(),args.evidence)
