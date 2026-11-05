#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Raspberry Pi-first discovery pages, accessible navigation and static metadata.

This build-time module adds no server process, tracking or runtime dependency.
Existing artwork, books, archive and privacy content is preserved by the builder.
"""
import base64
import hashlib
from html import escape as esc
import json
from pathlib import Path
import re
import shutil
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

SITE = 'https://daylightlinux.ch'
REPO = 'https://github.com/hamdyaea/Daylight-GNU-Linux'
EMAIL = 'info@daylightlinux.ch'
ROOT = Path(__file__).resolve().parent.parent
PAGES = [
 ('index.html','Accueil','Home'),
 ('raspberry-pi.html','Raspberry Pi','Raspberry Pi'),
 ('install.html','Installation','Installation'),
 ('download.html','Téléchargements','Downloads'),
 ('discover.html','Découvrir Daylight','Discover Daylight'),
 ('screenshots.html','Captures du bureau','Desktop screenshots'),
 ('try-online.html','Démo dans le navigateur','Browser demo'),
 ('wallpapers.html','Fonds d’écran','Wallpapers'),
 ('news.html','Actualités','News'),
 ('faq.html','Questions fréquentes','FAQ'),
 ('community.html','Communauté','Community'),
 ('information.html','Le projet','About the project'),
 ('books.html','Livres','Books'),
 ('press.html','Kit de présentation','Media kit'),
 ('old/index.html','Old · anciennes versions','Old · earlier versions'),
 ('privacy.html','Confidentialité','Privacy'),
]


def pick(lang, fr, en):
    return fr if lang == 'fr' else en


def anchor(url, label, cls=''):
    return '<a' + (f' class="{cls}"' if cls else '') + f' href="{esc(url, quote=True)}">{esc(label)}</a>'


def button(url, label, secondary=False):
    return anchor(url, label, 'button secondary' if secondary else 'button')


def para(text, cls=''):
    return '<p' + (f' class="{cls}"' if cls else '') + '>' + esc(text) + '</p>'


def code(text, lang, nowrap=False):
    label = pick(lang, 'Copier la commande', 'Copy command')
    pre = '<pre style="white-space:pre;overflow-x:auto">' if nowrap else '<pre>'
    return '<div class="codebox">' + pre + '<code>' + esc(text) + '</code></pre><button type="button" data-copy>' + label + '</button></div>'


def section(body, cls=''):
    return '<section class="section"><div class="wrap ' + cls + '">' + body + '</div></section>'


def head(title, lead, kicker='DAYLIGHT / RASPBERRY PI'):
    return '<section class="pagehead"><div class="wrap">' + para(kicker,'eyebrow') + '<h1>' + esc(title) + '</h1>' + para(lead,'lead') + '</div></section>'


def card(title, text, action='', tag=''):
    return '<article class="card">' + (para(tag,'tag') if tag else '') + '<h2>' + esc(title) + '</h2>' + para(text) + action + '</article>'


def build_social_image(out):
    """Compose a share preview from existing project artwork; no font is shipped."""
    image = ImageOps.fit(Image.open(ROOT/'assets/wallpapers/daylight-mountains.jpg').convert('RGB'),(1200,630))
    overlay = Image.new('RGBA', image.size)
    draw = ImageDraw.Draw(overlay)
    for x in range(1200):
        draw.line((x,0,x,630),fill=(6,14,17,int(235-110*x/1200)))
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(image)
    fontdir = Path('/usr/share/fonts/truetype/dejavu')
    def font(size, bold=False):
        name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
        choices = [fontdir/name, Path('/usr/share/fonts/TTF')/name]
        found = next((p for p in choices if p.exists()),None)
        return ImageFont.truetype(str(found),size) if found else ImageFont.load_default(size=size)
    draw.text((66,70),'DAYLIGHT GNU/LINUX',font=font(22,True),fill='#f4bd67')
    draw.text((62,172),'Your Raspberry Pi.',font=font(56,True),fill='#f4f5ee')
    draw.text((62,245),'A different horizon.',font=font(49),fill='#f4bd67')
    draw.text((66,405),'Fluxbox  /  Rust tools  /  Free software',font=font(24),fill='#e0e7e2')
    draw.text((66,525),'daylightlinux.ch',font=font(24),fill='#e0e7e2')
    path=out/'media/daylight-share.jpg';path.parent.mkdir(parents=True,exist_ok=True)
    image.convert('RGB').save(path,quality=88,optimize=True,progressive=True)


def enhance(out, release, evidence=None):
    version = release['version']
    prefix_for = lambda lang: '/fr/' if lang == 'fr' else '/'
    evidence = Path(evidence) if evidence else ROOT/'dist/site-evidence'/release['tag']
    shots=[]
    for source,name,fr,en in [
        ('live-test/desktop.png','desktop','Le bureau Fluxbox et Conky','The Fluxbox and Conky desktop'),
        ('desktop.png','settings','Les outils et réglages Daylight','Daylight tools and settings'),
        ('browser.png','browser','La démonstration dans un navigateur','The in-browser demonstration'),
    ]:
        source=evidence/source
        if source.is_file():
            with Image.open(source) as original:
                image=original.convert('RGB');image.thumbnail((1440,1000),Image.Resampling.LANCZOS)
                path=out/('media/screenshot-'+name+'.webp');image.save(path,quality=84,method=6)
            shots.append((path.name,fr,en,image.width,image.height))
    build_social_image(out)
    # The lightweight preview is separately validated and deployed as static assets.
    # Copy only its interface here; the large guest payload has its own manifest.
    live = out / 'live'
    live.mkdir(exist_ok=True)
    for name in ('index.html', 'demo.css', 'demo.js'):
        shutil.copyfile(ROOT / 'web-live' / name, live / name)
    shutil.copyfile(ROOT / 'assets/branding/daylight.svg', live / 'daylight.svg')
    page=(live/'index.html').read_text()
    for filename in ('demo.css','demo.js'):
        token=hashlib.sha256((live/filename).read_bytes()).hexdigest()[:12]
        page=page.replace('"'+filename+'"','"'+filename+'?v='+token+'"')
    (live/'index.html').write_text(page)
    # Content-addressed CSS/JS prevents old mobile styles surviving a deployment.
    assets={}
    for name, extra in [('style.css','discovery.css'),('main.js','discovery.js')]:
        data=(ROOT/'website'/name).read_bytes()+b'\n'+(ROOT/'website'/extra).read_bytes()
        digest=hashlib.sha256(data).hexdigest()[:12]
        destination='assets/v5/'+Path(name).stem+'.'+digest+Path(name).suffix
        (out/destination).write_bytes(data);assets[name]='/'+destination
    urls=[]
    descriptions={}
    for lang in ('en','fr'):
        p=prefix_for(lang)
        L=lambda name:p+name
        T=lambda fr,en:pick(lang,fr,en)
        title_home=T('Daylight Linux — le projet de Hamdy Abou El Anein','Daylight Linux — a project by Hamdy Abou El Anein')
        intro=T('Un bureau Fluxbox, des outils en Rust et une identité solaire pour votre Raspberry Pi OS 64 bits. Libre, personnalisable, et installé avec APT.','A Fluxbox desktop, Rust tools and a sunrise identity for your 64-bit Raspberry Pi OS. Free software, yours to customise, installed with APT.')
        rc_note=T('Version candidate : consultez les validations avant de l’installer sur une machine importante.','Release candidate: review the validation record before installing on an important machine.')
        pi_text=T('Le Raspberry Pi est au cœur du projet. Ajoutez Daylight à Raspberry Pi OS 64 bits : choisissez le bureau complet, ou seulement les outils sur une machine sans écran.','Raspberry Pi is at the heart of the project. Add Daylight to 64-bit Raspberry Pi OS: choose the desktop, or just the tools on a headless machine.')
        pc_text=T('Pas de Raspberry Pi sous la main ? Cette ISO live Debian AMD64 sert à découvrir et tester le bureau sur PC ou en machine virtuelle, sans installer Daylight. Ce n’est pas une image pour Raspberry Pi.','No Raspberry Pi at hand? This Debian AMD64 live ISO lets you discover and test the desktop on a PC or virtual machine without installing Daylight. It is not a Raspberry Pi image.')
        install_button=button(L('raspberry-pi.html'),T('Commencer sur Raspberry Pi','Start on Raspberry Pi'))
        live_button=button(REPO+'/releases/download/'+release['tag']+'/'+release['iso'],T('Télécharger le live PC pour tester','Download the PC live demo'),True)
        faq=[
          (T('Raspberry Pi ou PC : quelle version choisir ?','Raspberry Pi or PC: which version?'),T('Pour utiliser Daylight sur votre Pi, installez les paquets sur Raspberry Pi OS 64 bits. Le live PC AMD64 est une démonstration pour découvrir le bureau, pas une carte SD pour Raspberry Pi.','To use Daylight on your Pi, install the packages on 64-bit Raspberry Pi OS. The AMD64 PC live image is a desktop demonstration, not a Raspberry Pi SD-card image.')),
          (T('Quels systèmes sont pris en charge ?','Which systems are supported?'),T('La version actuelle cible Debian 12/13 et Raspberry Pi OS 64 bits compatible (ARM64). Le cœur a été exécuté sur Raspberry Pi 4. Cela ne certifie pas toutes les combinaisons de modèles, d’écrans et de pilotes. ARM 32 bits n’est pas pris en charge.','The current version targets Debian 12/13 and compatible 64-bit Raspberry Pi OS (ARM64). The core has run on Raspberry Pi 4. That does not certify every board, display and driver combination. 32-bit ARM is not supported.')),
          (T('Faut-il réinstaller Raspberry Pi OS ?','Must I reinstall Raspberry Pi OS?'),T('Non : Daylight ajoute ses paquets à un système compatible existant. Sauvegardez vos données et vérifiez le plan d’installation. Le bureau utilise une session X11 séparée et ne remplace pas automatiquement votre session actuelle.','No: Daylight adds packages to a compatible existing system. Back up your data and review the installation plan. The desktop uses a separate X11 session and does not automatically replace your current session.')),
          (T('Comment accéder au bureau après installation ?','How do I start the installed desktop?'),T('L’installateur propose de redémarrer et présélectionne Daylight lorsque le gestionnaire de connexion le permet. Si besoin, choisissez « Daylight GNU/Linux » à la connexion. Pour revenir au bureau précédent, lancez sudo daylight remove puis redémarrez. L’installation n’ajoute ni ne démarre un gestionnaire de connexion. Raspberry Pi OS Lite nécessite une activation graphique adaptée ; le mode core fonctionne sans écran.','The installer offers a reboot and selects Daylight when the login manager supports it. If needed, choose “Daylight GNU/Linux” at login. To return to the previous desktop, run sudo daylight remove and reboot. Installation does not add or start a display manager. Raspberry Pi OS Lite needs an appropriate graphical setup; core mode works without a display.')),
          (T('Est-ce déjà une version stable ?','Is this a stable release?'),T('Non, la série 5.0.0-rc est une version candidate. Les tests et leurs limites sont publics. Signaler votre matériel et les problèmes rencontrés aide à préparer une version stable, sans inventer de chiffres de performances.','No. The 5.0.0-rc series is a release candidate. Tests and limitations are public. Reporting hardware and problems helps work toward a stable release without inventing performance figures.')),
          (T('Puis-je le supprimer ?','Can I remove it?'),T('Oui : daylight remove --dry-run affiche la simulation, puis sudo daylight remove demande la suppression. Quittez d’abord la session Daylight. Aucun autoremove n’est lancé ; dépendances partagées, réglages personnels et configuration APT sont conservés. Ce n’est pas une restauration bit à bit.','Yes: daylight remove --dry-run previews removal, then sudo daylight remove requests it. Log out of Daylight first. It never runs autoremove; shared dependencies, personal settings and APT configuration remain. This is not a bit-for-bit restore.')),
          (T('Y a-t-il un suivi des utilisateurs ?','Does it track users?'),T('Le compteur de démarrages est un paquet distinct, désactivé par défaut. Le script d’installation ne l’active pas. Il compte des événements reçus, pas des utilisateurs uniques. Le site n’ajoute aucun outil analytique publicitaire ; les intermédiaires réseau peuvent voir les connexions.','The boot counter is a separate package, disabled by default. The installer does not enable it. It counts received events, not unique users. The site adds no advertising analytics; network intermediaries can still observe connections.')),
          (T('La démo web utilise-t-elle le Raspberry Pi du projet ?','Does the web demo run on the project’s Raspberry Pi?'),T('Non. La démo légère Alpine s’exécute dans votre navigateur avec WebAssembly, sans compte. Le Pi sert uniquement ses fichiers. La démonstration ne nécessite aucun compte et ne lance aucune machine virtuelle sur notre Pi.','No. The lightweight Alpine demo runs inside your browser with WebAssembly, without an account. The Pi only serves its files. The demo requires no account and runs no virtual machine on our Pi.')),
        ]
        def question_list(items):
            return ''.join('<details class="faq-item"><summary>'+esc(q)+'</summary>'+para(a)+'</details>' for q,a in items)
        def photo(shot):
            name,fr,en,w,h=shot
            return '<figure class="shot"><a href="/media/'+name+'"><img src="/media/'+name+'" alt="'+esc(T(fr,en),quote=True)+'" width="'+str(w)+'" height="'+str(h)+'" loading="lazy"></a><figcaption>'+esc(T(fr,en))+'</figcaption></figure>'
        # Keep the established content for these pages; replace the wrapper globally.
        bodies={}
        for name,_,_ in PAGES:
            old=out/(p.lstrip('/')+name)
            if old.exists():
                match=re.search(r'<main id="main">(.*?)</main>',old.read_text(),re.S)
                if match:bodies[name]=match.group(1)
        body='<section class="hero pi-hero"><div class="wrap">'+para('DAYLIGHT GNU/LINUX · '+version,'pill')+'<h1>'+T('Votre Raspberry Pi.<br><em>Un autre horizon.</em>','Your Raspberry Pi.<br><em>A different horizon.</em>')+'</h1>'+para(intro,'lead')+'<div class="actions">'+install_button+button('#daylight-demo',T('Essayer ici','Try it here'),True)+'</div>'+para('The lighter you become, the more you are able to run.','small')+'</div></section>'
        body+=section('<div id="daylight-demo" class="home-demo"><h2>'+T('Démarrez Daylight ici.','Start Daylight right here.')+'</h2>'+para(T('Un vrai bureau Linux léger, directement dans votre navigateur. Aucun compte nécessaire.','A real lightweight Linux desktop in your browser. No account needed.'),'lead')+'<iframe title="Daylight Start — Linux live" src="/live/?lang='+lang+'&amp;embed=1" loading="lazy" allow="fullscreen" referrerpolicy="no-referrer" class="daylight-live-frame"></iframe>'+para(T('Aperçu expérimental Alpine/Fluxbox. La version installable reste basée sur Raspberry Pi OS.','Experimental Alpine/Fluxbox preview. The installable edition remains based on Raspberry Pi OS.'),'small')+'</div>')
        body+='<div class="wrap"><div class="strip">'+''.join('<div><strong>'+a+'</strong><span>'+b+'</span></div>' for a,b in [('Raspberry Pi','ARM64 / Raspberry Pi OS'),('Fluxbox',T('Un bureau à vous','A desktop of your own')),('Rust',T('Des outils à la demande','Tools on demand')),('GPLv3',T('Libre et ouvert','Free and open'))])+'</div></div>'
        if shots:
            body+=section('<div class="split"><div>'+para(T('À DÉCOUVRIR','TAKE A LOOK'),'eyebrow')+'<h2>'+T('Un petit ordinateur.<br>De grandes possibilités.','A small computer.<br>Room to make it yours.')+'</h2>'+para(pi_text,'lead')+para(T('Capture de démonstration : ce n’est pas une mesure des performances Raspberry Pi.','Demonstration screenshot, not a Raspberry Pi performance benchmark.'),'small')+'</div>'+photo(shots[0])+'</div>')
        uses=[(T('Retrouver le plaisir de Linux','Rediscover Linux'),T('Un menu simple, un terminal à portée de main et des fichiers de configuration lisibles. Explorez un bureau qui reste compréhensible.','A straightforward menu, a terminal close at hand and readable configuration files. Explore a desktop you can understand.')),(T('Personnaliser votre Pi','Make your Pi your own'),T('Choisissez votre paysage, votre profil Conky et vos outils. Gardez Raspberry Pi OS comme base au lieu de tout remplacer.','Choose a landscape, a Conky profile and your tools. Keep Raspberry Pi OS as the foundation instead of replacing everything.')),(T('Construire avec le projet','Build with the project'),T('Lisez le Rust, testez sur votre matériel et partagez une amélioration. Débutants curieux et utilisateurs expérimentés ont leur place.','Read the Rust, test on your hardware and contribute an improvement. Curious beginners and experienced users are welcome.'))]
        body+=section('<h2>'+T('Fait pour les curieux.','For curious minds.')+'</h2><div class="grid">'+''.join(card(a,b,tag='0'+str(i+1)) for i,(a,b) in enumerate(uses))+'</div><div class="actions">'+button(L('discover.html'),T('Pourquoi Daylight ?','Why Daylight?'),True)+button(L('community.html'),T('Rejoindre le projet','Join the project'),True)+'</div>')
        body+=section('<div class="split"><div><h2>'+T('Installer le bureau Daylight','Install the Daylight desktop')+'</h2>'+para(T('La première commande télécharge le script. La seconde lance l’installation du bureau Daylight.','The first command downloads the script. The second starts the Daylight desktop installation.'),'lead')+button(L('install.html'),T('Le guide d’installation','Installation guide'),True)+'</div>'+code("sudo curl -fsSLO https://daylightlinux.ch/install.sh\nsudo sh install.sh --desktop --yes",lang,nowrap=True)+'</div>')
        body+=section('<h2>'+T('Avant de vous lancer','Before you start')+'</h2>'+question_list(faq[:3])+para(rc_note,'small')+anchor(L('faq.html'),T('Toutes les réponses →','All answers →')))
        body+=section('<div class="cta"><h2>'+T('Votre prochain projet commence ici.','Your next project starts here.')+'</h2>'+para(T('Découvrez Daylight, montrez votre bureau et aidez-nous à le rendre meilleur.','Discover Daylight, share your desktop and help make it better.'),'lead')+'<div class="actions">'+install_button+button(L('community.html'),T('Partager et contribuer','Share and contribute'),True)+'</div></div>')
        bodies['index.html']=body+T('<section class="section"><div class="wrap prose"><h2>Un projet de Hamdy Abou El Anein</h2><p>Je développe Daylight GNU/Linux pour proposer un environnement Linux léger et ouvert. Le projet rassemble un bureau Fluxbox, des outils et une documentation consultable avec les sources.</p><p><a href="/fr/information">Découvrir Hamdy Abou El Anein et l’histoire de Daylight Linux</a></p></div></section>','<section class="section"><div class="wrap prose"><h2>A project by Hamdy Abou El Anein</h2><p>I develop Daylight GNU/Linux to provide a lightweight, open Linux environment. The project brings together a Fluxbox desktop, tools and documentation alongside the source code.</p><p><a href="/information">Meet Hamdy Abou El Anein and discover the Daylight Linux story</a></p></div></section>')
        bodies['download.html']=head(T('Installer Daylight sur Raspberry Pi','Install Daylight on Raspberry Pi'),pi_text)+section('<article class="card featured"><h2>Raspberry Pi OS · ARM64</h2>'+para(pi_text,'lead')+'<div class="actions">'+install_button+button(L('install.html'),T('Installer avec APT','Install with APT'),True)+'</div></article><div class="actions">'+button(L('index.html')+'#daylight-demo',T('Essayer dans le navigateur','Try in your browser'),True)+button(REPO+'/releases/tag/'+release['tag'],T('Archives et sommes de contrôle','Release archives and checksums'),True)+'</div>')
        bodies['raspberry-pi.html']=head(T('Donnez un autre horizon à votre Pi.','Give your Pi a different horizon.'),pi_text)+section('<div class="grid two">'+card(T('Le bureau pour explorer','A desktop to explore'),T('Fluxbox, Conky, un terminal personnalisé et les applications Daylight. Une session distincte sur votre Raspberry Pi OS existant.','Fluxbox, Conky, a personalised terminal and Daylight applications. A separate session on your existing Raspberry Pi OS.'),button(L('install.html')+'#desktop',T('Installer le bureau','Install the desktop')),'DESKTOP')+card(T('Les outils sans bureau','Tools without a desktop'),T('Pour un Pi sans écran ou un serveur : gardez seulement le cœur Rust et les commandes locales. Aucune interface graphique à démarrer.','For a headless Pi or a server: keep just the Rust core and local commands. No graphical interface to start.'),button(L('install.html')+'#core',T('Choisir le mode core','Choose core mode'),True),'CORE')+'</div><div class="prose"><h2>'+T('Vérifier avant d’installer','Check before installing')+'</h2>'+para(T('Le gestionnaire de paquets doit annoncer arm64. Un processeur 64 bits peut héberger un OS 32 bits : c’est l’architecture du système installé qui compte.','The package manager must report arm64. A 64-bit processor may run a 32-bit OS: what matters is the installed system’s architecture.'))+code('dpkg --print-architecture\ncat /etc/os-release',lang)+para(T('Base ciblée : Debian 12/13 ou Raspberry Pi OS compatible. Le cœur natif a été testé sur Raspberry Pi 4 ; la session graphique physique reste à valider sur chaque configuration.','Target base: Debian 12/13 or compatible Raspberry Pi OS. The native core was tested on Raspberry Pi 4; physical graphical sessions still need validation on each configuration.'))+'<h2>'+T('Après l’installation','After installation')+'</h2>'+para(faq[3][1])+code('daylight info\ndaylight doctor\ndaylight control-center',lang)+'<h2>'+T('Vous avez essayé sur votre Pi ?','Tried it on your Pi?')+'</h2>'+para(T('Indiquez le modèle, l’architecture et ce qui fonctionne. Un retour précis est plus utile qu’un score isolé. Ne publiez pas d’adresse IP, de numéro de série ou de secrets.','Tell us the model, architecture and what works. A precise report is more useful than an isolated score. Do not publish IP addresses, serial numbers or secrets.'))+button(REPO+'/issues/new?template=hardware_report.yml',T('Partager un retour matériel','Share a hardware report'),True)+'</div>')
        bodies['discover.html']=head(T('Linux, à votre façon.','Linux, your way.'),intro)+section('<div class="grid">'+''.join(card(a,b) for a,b in uses)+'</div><div class="prose"><h2>'+T('Ce que vous trouverez','What you will find')+'</h2>'+para(T('Un bureau Fluxbox, un moniteur Conky, des paysages Daylight et un terminal avec logo ASCII. Les utilitaires Rust regroupent mots de passe, températures, dates, réseau local et alarmes ; les jeux sont facultatifs. Les fenêtres natives utilisent YAD uniquement à la demande.','A Fluxbox desktop, Conky monitor, Daylight landscapes and an ASCII-branded terminal. Rust utilities cover passwords, temperatures, dates, local networking and alarms; games are optional. Native windows use YAD only on demand.'))+'<h2>'+T('Une base familière, pas une boîte noire','A familiar foundation, not a black box')+'</h2>'+para(T('Raspberry Pi OS reste identifiable. Daylight se gère en paquets Debian et conserve ses réglages séparément. Son code et ses tests sont publics sous GPLv3, avec les licences tierces préservées.','Raspberry Pi OS remains identifiable. Daylight is managed as Debian packages and keeps its settings separate. Its code and tests are public under GPLv3, with third-party licenses preserved.'))+'<h2>'+T('Léger : un objectif que l’on vérifie','Lightweight: a goal to verify')+'</h2>'+para(T('Pas d’Electron pour les outils, pas de serveur de réglages permanent, pas de requête réseau à chaque terminal. Les résultats dépendent du matériel et des services actifs : nous ne promettons pas un pourcentage d’accélération sans mesure comparable.','No Electron-based toolkit, no permanent settings server and no network request whenever you open a terminal. Results depend on hardware and running services: we do not promise a speedup percentage without comparable measurements.'))+'<div class="actions">'+install_button+button(L('screenshots.html'),T('Voir le bureau','See the desktop'),True)+'</div></div>')
        bodies['screenshots.html']=head(T('Regardez avant d’installer.','See it before installing.'),T('Captures réelles de l’édition live PC publiée. Elles présentent le bureau et les outils, pas des performances mesurées sur Raspberry Pi.','Actual screenshots from the published PC live edition. They show the desktop and tools, not Raspberry Pi performance measurements.'),'DAYLIGHT / '+version)+section('<div class="screenshots-grid">'+''.join(photo(s) for s in shots)+'</div>'+('' if shots else para(T('Les captures vérifiées se trouvent dans les fichiers de la version publiée.','Verified screenshots are available in the published release files.')))+'<div class="actions">'+install_button+button(REPO+'/releases/tag/'+release['tag'],T('Originaux et validations','Originals and validation'),True)+'</div>')
        bodies['faq.html']=head(T('Les réponses avant le premier démarrage.','Answers before your first boot.'),T('Compatibilité, installation, suppression et confidentialité : les limites sont aussi importantes que les fonctionnalités.','Compatibility, installation, removal and privacy: the boundaries matter as much as the features.'))+section(question_list(faq),'prose')
        share='<button class="button secondary" type="button" data-share data-share-url="'+SITE+L('raspberry-pi.html')+'">'+T('Partager Daylight','Share Daylight')+'</button>'
        bodies['community.html']=head(T('Un projet libre grandit avec ses utilisateurs.','Free software grows with its users.'),T('Essayez, racontez, améliorez. Pas besoin d’être expert pour faire avancer Daylight.','Try it, tell us about it, improve it. You do not need to be an expert to help Daylight grow.'))+section('<div class="grid">'+card(T('Tester sur votre matériel','Test your hardware'),T('Votre modèle de Pi, la version de l’OS et le résultat d’un essai : des informations utiles, sans données personnelles.','Your Pi model, OS version and test outcome: useful information without personal data.'),button(REPO+'/issues/new?template=hardware_report.yml',T('Retour matériel','Hardware report'),True))+card(T('Signaler un problème','Report a problem'),T('Un résultat inattendu ? Expliquez les étapes, le résultat attendu et ce qui s’est passé. Masquez les secrets dans les journaux.','Unexpected behaviour? Describe the steps, expected result and actual outcome. Remove secrets from logs.'),button(REPO+'/issues/new?template=bug_report.yml',T('Ouvrir un signalement','Report a bug'),True))+card(T('Proposer une amélioration','Suggest an improvement'),T('Documentation, traduction, ergonomie, code ou thème : commencez par une proposition claire et limitée.','Documentation, translation, usability, code or themes: start with a clear, focused proposal.'),button(REPO+'/issues/new?template=feature_request.yml',T('Proposer une idée','Propose an idea'),True))+'</div><div class="prose"><h2>'+T('Faites découvrir votre bureau','Share your desktop')+'</h2>'+para(T('Présentez votre propre configuration, expliquez pourquoi vous l’avez choisie et partagez le lien du projet. Mentionnez qu’il s’agit d’une version candidate et masquez les informations personnelles de vos captures.','Show your own setup, explain why you chose it and share the project link. Mention that it is a release candidate and hide personal information in screenshots.'))+'<div class="actions">'+share+button(REPO,T('Suivre le projet sur GitHub','Follow the project on GitHub'),True)+button(L('press.html'),T('Kit de présentation','Media kit'),True)+'</div><h2>'+T('Contribuer sans deviner','Contribute with clear guidance')+'</h2>'+para(T('Le guide décrit les tests, les petites contributions bienvenues et les règles de confidentialité. Les performances et la compatibilité sont documentées à partir d’essais, pas de témoignages inventés.','The guide covers tests, useful small contributions and privacy rules. Performance and compatibility are documented from tests, not invented testimonials.'))+anchor(REPO+'/blob/master/CONTRIBUTING.md',T('Lire le guide de contribution →','Read the contribution guide →'))+'<h2>'+T('Suivre les nouveautés sans compte','Follow updates without an account')+'</h2>'+para(T('Ajoutez notre flux RSS à votre lecteur. Aucun abonnement email, traqueur ou cookie analytique n’est nécessaire.','Add our RSS feed to your reader. No email signup, tracker or analytics cookie is needed.'))+button(L('feed.xml'),T('Flux RSS des actualités','News RSS feed'),True)+'</div>')
        bodies['information.html']=head(T('Hamdy Abou El Anein, créateur de Daylight Linux.','Hamdy Abou El Anein, creator of Daylight Linux.'),T('Daylight GNU/Linux est le projet libre de Hamdy Abou El Anein, son fondateur et développeur.','Daylight GNU/Linux is the free-software project of its founder and developer, Hamdy Abou El Anein.'))+section('<div class="prose"><h2>'+'The lighter you become, the more you are able to run.'+'</h2>'+para(pi_text)+'<h2>'+T('Une évolution, pas un oubli','Moving forward, keeping the history')+'</h2>'+para(T('Les premières versions étaient distribuées comme images complètes. La version 5 apporte des paquets Debian, des outils Rust et une session de bureau distincte. Les anciennes versions et leur historique restent disponibles dans Old.','Earlier versions were distributed as complete images. Version 5 brings Debian packages, Rust tools and a separate desktop session. Earlier releases and their history remain available under Old.'))+'<h2>'+T('Des choix explicites','Explicit choices')+'</h2>'+para(T('GPLv3 pour le code Daylight, licences tierces conservées, télémétrie facultative désactivée par défaut et code public. La légèreté reste un objectif technique ; les validations et leurs limites sont consultables.','GPLv3 for Daylight code, preserved third-party licenses, optional telemetry disabled by default and public source. Low overhead remains a technical goal; validations and their limits are available.'))+'<div class="actions">'+button(REPO,T('Voir les sources','Read the source'))+button(L('old/index.html'),'Old',True)+button(L('books.html'),T('Les livres du fondateur','Books by the founder'),True)+'</div>'+T('<h2>Hamdy Abou El Anein, fondateur et développeur</h2><p>Ingénieur systèmes Linux senior et formateur en Suisse, je développe Daylight GNU/Linux pour partager mon intérêt pour Linux et les logiciels libres.</p><p><a href="https://software-coders.ch/hamdy-abou-el-anein/">Mon parcours et mes projets</a> · <a href="https://software-coders.ch/#formations">Mes formations informatiques en ligne en Suisse</a> · <a href="https://astrometry.ch/about">Mon projet pédagogique Astrometry</a></p>','<h2>Hamdy Abou El Anein, founder and developer</h2><p>I am a senior Linux systems engineer and IT trainer based in Switzerland. I develop Daylight GNU/Linux to share my interest in Linux and free software.</p><p><a href="https://software-coders.ch/hamdy-abou-el-anein/">My background and projects</a> · <a href="https://software-coders.ch/#formations">Online IT training in Switzerland</a> · <a href="https://astrometry.ch/about">My Astrometry education project</a></p>')+T('<h2>Une publication signée dans Linux Journal</h2><p>Le 13 mars 2019, j’ai présenté la version 3 de Daylight Linux dans Linux Journal. Cet article documente une étape antérieure du projet ; les instructions actuelles se trouvent sur ce site.</p><p><a href="https://www.linuxjournal.com/content/foss-project-spotlight-daylight-linux-version-3">Lire mon article sur Daylight Linux dans Linux Journal</a></p>','<h2>My article in Linux Journal</h2><p>On March 13, 2019, I introduced Daylight Linux version 3 in Linux Journal. The article documents an earlier stage of the project; current installation instructions are available on this website.</p><p><a href="https://www.linuxjournal.com/content/foss-project-spotlight-daylight-linux-version-3">Read my Daylight Linux article in Linux Journal</a></p>')+'<h2>Contact</h2>'+anchor('mailto:'+EMAIL,EMAIL)+'</div>')
        bodies['news.html']=head(T('Les nouvelles de Daylight','Daylight news'),T('Versions publiées, évolution du site et prochaines étapes vérifiables.','Published releases, website changes and verifiable next steps.'))+section('<div class="prose"><article><p class="eyebrow">2026-11-02 / WEBSITE</p><h2>'+T('Raspberry Pi au premier plan','Raspberry Pi takes the lead')+'</h2>'+para(T('Un parcours dédié au Pi, toutes les pages accessibles sur mobile, un guide de découverte et des retours matériels structurés. Le live PC est présenté comme un moyen de tester, pas comme la destination principale.','A dedicated Pi pathway, every page accessible on mobile, a discovery guide and structured hardware feedback. The PC live edition is presented as a way to test, not the main destination.'))+anchor(L('raspberry-pi.html'),T('Découvrir le parcours Raspberry Pi →','Explore the Raspberry Pi pathway →'))+'</article><article class="news-entry"><p class="eyebrow">RELEASE</p><h2>Daylight GNU/Linux '+esc(version)+'</h2>'+para(T('La version publiée et ses fichiers restent identifiés par le manifeste du projet. Il s’agit d’une version candidate, avec paquets ARM64/AMD64, image live PC et preuves de validation.','The published version and files are identified by the project manifest. This is a release candidate, with ARM64/AMD64 packages, a PC live image and validation evidence.'))+anchor(REPO+'/releases/tag/'+release['tag'],T('Notes et fichiers de la version →','Release notes and files →'))+'</article><div class="actions">'+button(L('feed.xml'),T('Suivre avec RSS','Follow with RSS'),True)+button(L('community.html'),T('Aider la prochaine version','Help with the next release'),True)+'</div></div>')
        blurb=T('Daylight GNU/Linux ajoute un bureau Fluxbox et des outils Rust à Raspberry Pi OS 64 bits. Le projet libre de Hamdy Abou El Anein se distribue en paquets Debian ; un live PC AMD64 permet de le découvrir sans installation. La série 5.0.0-rc est une version candidate.','Daylight GNU/Linux adds a Fluxbox desktop and Rust tools to 64-bit Raspberry Pi OS. The free-software project by Hamdy Abou El Anein is distributed as Debian packages; an AMD64 PC live image provides a way to explore without installation. The 5.0.0-rc series is a release candidate.')
        bodies['press.html']=head(T('Présenter Daylight, simplement.','Introduce Daylight, simply.'),T('Une présentation réutilisable, le logo et de vraies captures pour les passionnés, associations et médias Linux.','A reusable introduction, the logo and actual screenshots for enthusiasts, user groups and Linux media.'))+section('<div class="prose"><h2>'+T('Le projet en quelques lignes','The project in a few lines')+'</h2>'+para(blurb,'lead')+'<div class="actions">'+button('/media/daylight-media-kit.zip',T('Télécharger le kit de présentation','Download the media kit'))+share+'</div><h2>'+T('Des faits, pas des promesses','Facts, not promises')+'</h2>'+para(T('Cible principale : Raspberry Pi OS 64 bits. Bureau : Fluxbox et Conky. Outils : Rust et fenêtres YAD. Licence Daylight : GPLv3. État : version candidate. Les captures live sont réalisées sur PC/VM, pas présentées comme des benchmarks Pi.','Primary target: 64-bit Raspberry Pi OS. Desktop: Fluxbox and Conky. Tools: Rust and YAD windows. Daylight license: GPLv3. Status: release candidate. Live screenshots come from PC/VM tests and are not presented as Pi benchmarks.'))+'<h2>'+T('Crédits et contact','Credits and contact')+'</h2>'+para(T('Conservez les attributions. Le kit ne contient aucune police de caractères. Les licences des images et composants tiers restent distinctes de celle du code.','Keep attributions. The kit includes no font files. Artwork and third-party licenses remain separate from the code license.'))+anchor('mailto:'+EMAIL,EMAIL)+'</div>')
        # The public path is an actual graphical browser guest, with no account.
        launch = '<a class="button" href="/live/?lang=' + lang + '" target="_blank" rel="noopener">' + T('Ouvrir le bureau graphique — sans compte', 'Open the graphical desktop — no account') + '</a>'
        bodies['try-online.html'] = head(
            T('Un bureau Linux dans une fenêtre.', 'A Linux desktop inside a window.'),
            T('Ouvrez la démo, puis cliquez sur Démarrer : le terminal s’ouvre au premier plan. Aucun compte GitHub, aucune installation, aucun terminal à configurer.', 'Open the demo, then click Start: your terminal opens in the foreground. No GitHub account, no installation and no terminal setup.'))
        bodies['try-online.html'] += section('<article class="card featured"><p class="tag">ALPINE + FLUXBOX / WEBASSEMBLY</p><h2>' + T('Un véritable bureau graphique, pas une imitation.', 'A real graphical desktop, not an imitation.') + '</h2>' + para(T('Retrouvez le paysage Daylight, des fenêtres déplaçables, la barre des tâches, un menu, un terminal et une véritable calculatrice graphique. La barre contient seulement Démarrer, Redémarrer et Stop. Les applications restent accessibles par le menu du bureau.', 'Explore the Daylight landscape, movable windows, taskbar, menu, terminal and a real graphical calculator. The toolbar contains only Start, Restart and Stop. Applications remain accessible from the desktop menu.'), 'lead') + '<div class="actions">' + launch + '</div>' + para(T('Le système démarre uniquement après votre clic : environ 42 Mo à télécharger et 256 Mio de RAM pour le Linux invité, plus les besoins du navigateur. Ordinateur et clavier recommandés.', 'The system starts only after your click: about 42 MB to download and 256 MiB RAM for the Linux guest, plus browser overhead. A computer and keyboard are recommended.'), 'small note') + '</article>')
        preview = ROOT / 'website/assets/web-live-preview.webp'
        if preview.is_file():
            preview_name = 'web-live-preview-' + hashlib.sha256(preview.read_bytes()).hexdigest()[:12] + '.webp'
            shutil.copyfile(preview, out / 'media' / preview_name)
            bodies['try-online.html'] += section('<figure class="shot"><img src="/media/' + preview_name + '" alt="' + T('Capture réelle du bureau Alpine, du terminal et de la calculatrice dans la démo web', 'Actual Alpine desktop, terminal and calculator in the browser demo') + '" width="1024" height="768" loading="lazy"><figcaption>' + T('Capture réelle de la démo légère Alpine ; le système installé sur Raspberry Pi reste basé sur Debian.', 'Actual lightweight Alpine preview; the installable Raspberry Pi system remains Debian-based.') + '</figcaption></figure>')
        bodies['try-online.html'] += section('<div class="grid two">' + card(T('Le calcul se fait chez vous.', 'Computing happens on your device.'), T('Le processeur et la mémoire utilisés sont ceux de votre navigateur. Notre Raspberry Pi distribue seulement des fichiers statiques : aucun conteneur ou bureau partagé public n’y est lancé.', 'CPU and memory come from your browser. Our Raspberry Pi only serves static files: it does not launch a public container or shared desktop.')) + card(T('Une session temporaire et isolée.', 'A temporary, isolated session.'), T('Pas de compte, pas de disque personnel partagé, pas de relais réseau externe pour l’invité et pas de télémétrie. Fermer, arrêter ou réinitialiser efface la session. N’y entrez pas de données sensibles.', 'No account, no shared personal disk, no external guest-network relay and no telemetry. Closing, stopping or resetting discards the session. Do not enter sensitive data.')) + '</div><div class="callout">' + esc(T('Cette démo expérimentale est un Alpine x86 allégé avec Fluxbox. Elle sert à découvrir l’esprit Daylight : ce n’est ni l’image Debian complète ni une émulation de Raspberry Pi, et elle n’inclut pas tous les outils Rust.', 'This experimental demo is a stripped-down Alpine x86 guest with Fluxbox. It introduces the Daylight experience: it is neither the complete Debian image nor Raspberry Pi emulation, and does not include every Rust tool.')) + '</div><div class="actions">' + button(L('raspberry-pi.html'),T('L’utiliser sur mon Raspberry Pi', 'Use it on my Raspberry Pi')) + button(L('index.html')+'#daylight-demo',T('Tester le live PC Debian complet', 'Try the full Debian PC live edition'),True) + '</div>')
        bodies['try-online.html'] += section('<details><summary>' + T('Option développeur : ISO complète dans un environnement privé', 'Developer option: full ISO in a private environment') + '</summary>' + para(T('Le parcours QEMU/noVNC ou Codespaces est facultatif. Codespaces ouvre un environnement de développement et demande un compte GitHub ; il peut occasionner des frais. Pour le bureau graphique public sans compte, utilisez le bouton ci-dessus.', 'QEMU/noVNC or Codespaces is optional. Codespaces opens a development environment and requires a GitHub account; charges may apply. For the public no-account graphical desktop, use the button above.')) + anchor(REPO+'/blob/master/demo/README.md',T('Documentation technique de l’option complète', 'Full-edition technical documentation')) + '</details>', 'prose')
        bodies['try-online.html']=head(T('Essayez Daylight directement sur l’accueil.','Try Daylight directly on the home page.'),T('Aucun compte, aucune ISO à télécharger : le bureau Linux se lance dans votre navigateur.','No account and no ISO download: the Linux desktop starts in your browser.'))+section('<div class="cta"><h2>Daylight Start</h2>'+para(T('Le bureau graphique se trouve sur la page d’accueil, devant le paysage Daylight. Démarrer, Redémarrer et Stop sont les seuls boutons nécessaires.','The graphical desktop is on the home page, in front of the Daylight landscape. Start, Restart and Stop are the only controls.'),'lead')+button(L('index.html')+'#daylight-demo',T('Démarrer sur l’accueil','Start on the home page'))+'</div>')
        # Add session guidance and distinct anchors to the existing, verified installer guide.
        bodies['install.html']=bodies['install.html'].replace('<h1>','<h1>',1).replace('<p>Desktop :</p>', '<h3 id="desktop">'+T('Bureau Raspberry Pi','Raspberry Pi desktop')+'</h3>').replace('<p>Desktop + games :</p>','<h3>'+T('Bureau et jeux facultatifs','Desktop and optional games')+'</h3>')
        bodies['install.html']=bodies['install.html'].replace(code('sudo sh install-daylight.sh --core --yes',lang),'<h3 id="core">'+T('Cœur CLI : Pi sans écran ou serveur','CLI core: headless Pi or server')+'</h3>'+code('sudo sh install-daylight.sh --core --yes',lang))
        bodies['install.html']+=section('<div class="prose"><h2>'+T('Ouvrir la session Daylight','Open the Daylight session')+'</h2>'+para(faq[3][1])+anchor(L('faq.html'),T('Compatibilité et questions fréquentes →','Compatibility and frequently asked questions →'))+'</div>')
        # Per-page descriptions and titles: no keyword stuffing or fabricated ratings.
        for name,fr,en in PAGES:
            label=T(fr,en)
            if name not in bodies:raise ValueError('Missing body for '+name)
            body=bodies[name]
            title=title_home if name=='index.html' else label+' — Daylight Linux'
            if name=='information.html': title='Hamdy Abou El Anein — '+T('Le projet Daylight Linux','About Daylight Linux')
            lead=re.search(r'<p class="lead">(.*?)</p>',body,re.S)
            description=re.sub('<[^>]+>','',lead.group(1)) if lead else T('Explorez '+fr+' sur Daylight GNU/Linux, le projet libre pour Raspberry Pi.','Explore '+en+' in Daylight GNU/Linux, the free-software Raspberry Pi project.')
            description=__import__('html').unescape(description)
            if name=='index.html': description=T('Daylight GNU/Linux, le projet libre de Hamdy Abou El Anein : bureau léger Fluxbox, outils Rust et démonstration Linux dans le navigateur.','Daylight GNU/Linux by Hamdy Abou El Anein: a lightweight Fluxbox desktop, Rust tools and a browser-based Linux demonstration.')
            if name != 'index.html': description = label + ' — ' + description
            # Keep a complete sentence where practical; full visible text remains on-page.
            if len(description)>190:description=description[:187].rsplit(' ',1)[0]+'…'
            canonical=SITE+p+('' if name=='index.html' else name)
            descriptions[(lang,name)]=description
            nav=[]
            for dest,fr_label,en_label in PAGES:
                current=' aria-current="page"' if dest==name else ''
                nav.append('<a href="'+L(dest)+'"'+current+'>'+esc(T(fr_label,en_label))+'</a>')
            other=('/' if lang=='fr' else '/fr/')+name
            language_link='<a class="language-switch" lang="'+('en' if lang=='fr' else 'fr')+'" hreflang="'+('en' if lang=='fr' else 'fr')+'" href="'+other+'">'+('EN' if lang=='fr' else 'FR')+'</a>'
            primary=''.join(anchor(L(dest),text) for dest,text in [('raspberry-pi.html','Raspberry Pi'),('community.html',T('Communauté','Community'))])
            header='<header class="header"><div class="wrap"><div class="nav pi-nav"><a class="brand" href="'+L('index.html')+'"><img src="/assets/v5/daylight.svg" alt="" width="42" height="42"><span>Daylight</span><span>GNU/LINUX</span></a><nav class="quick-links" aria-label="'+T('Accès rapide','Quick links')+'">'+primary+'</nav><div class="nav-controls">'+language_link+'<details class="site-menu"><summary><span class="menu-lines" aria-hidden="true">☰</span> Menu<span class="menu-extra"> · '+T('toutes les pages','all pages')+'</span></summary><nav class="menu-panel" aria-label="'+T('Toutes les pages','All pages')+'">'+''.join(nav)+'</nav></details></div></div></div></header>'
            footer='<footer class="footer"><div class="wrap"><div class="footgrid"><div><a class="brand" href="'+L('index.html')+'">Daylight GNU/Linux</a>'+para('The lighter you become, the more you are able to run.')+para(anchor(L('information.html'),'Hamdy Abou El Anein')+' · GPLv3')+anchor('mailto:'+EMAIL,EMAIL)+'</div><nav class="footer-pages" aria-label="'+T('Plan du site','Site directory')+'">'+''.join(nav)+'</nav></div><div class="footer-bottom">'+anchor(L('feed.xml'),'RSS')+' · '+anchor(REPO,'GitHub')+' · '+anchor(L('privacy.html'),T('Confidentialité','Privacy'))+'</div></div></footer>'
            structured={'@context':'https://schema.org','@graph':[{'@type':'WebSite','@id':SITE+'/#website','url':SITE+'/','name':'Daylight GNU/Linux','inLanguage':['en','fr'],'creator':{'@id':'https://software-coders.ch/hamdy-abou-el-anein/#person'}},{'@type':'WebPage','@id':canonical+'#page','url':canonical,'name':title,'description':description,'inLanguage':lang,'isPartOf':{'@id':SITE+'/#website'}},{'@type':'SoftwareSourceCode','@id':SITE+'/#project','name':'Daylight GNU/Linux','codeRepository':REPO,'license':'https://www.gnu.org/licenses/gpl-3.0.html','programmingLanguage':'Rust','version':version,'runtimePlatform':'Raspberry Pi OS 64-bit; Debian 12/13','author':{'@type': 'Person', '@id': 'https://software-coders.ch/hamdy-abou-el-anein/#person', 'name': 'Hamdy Abou El Anein', 'url': 'https://software-coders.ch/hamdy-abou-el-anein/', 'sameAs': ['https://github.com/hamdyaea']}}]}
            if name=='information.html': structured['@graph'][1]['about']={'@id':'https://software-coders.ch/hamdy-abou-el-anein/#person'}
            if name != 'index.html':
                crumb_label=T('Accueil','Home')
                structured['@graph'].append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':crumb_label,'item':SITE+p},{'@type':'ListItem','position':2,'name':label,'item':canonical}]})
                body='<nav class="wrap" aria-label="'+T('Fil d’Ariane','Breadcrumb')+'"><p><a href="'+p+'">'+crumb_label+'</a> <span aria-hidden="true">›</span> <span aria-current="page">'+esc(label)+'</span></p></nav>'+body
            payload=json.dumps(structured,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
            sha=base64.b64encode(hashlib.sha256(payload.encode()).digest()).decode()
            csp="default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self' 'sha256-"+sha+"'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'self'"
            metadata='<meta name="author" content="Hamdy Abou El Anein"><meta name="description" content="'+esc(description,quote=True)+'"><meta name="referrer" content="no-referrer"><meta name="theme-color" content="#0b1012"><meta http-equiv="Content-Security-Policy" content="'+esc(csp,quote=True)+'"><link rel="canonical" href="'+canonical+'">'
            for code_lang in ('en','fr'):
                alternate=SITE+prefix_for(code_lang)+('' if name=='index.html' else name)
                metadata+='<link rel="alternate" hreflang="'+code_lang+'" href="'+alternate+'">'
            metadata+='<link rel="alternate" hreflang="x-default" href="'+SITE+'/'+('' if name=='index.html' else name)+'"><link rel="alternate" type="application/rss+xml" title="Daylight news" href="'+L('feed.xml')+'">'
            for prop,value in [('og:type','website'),('og:site_name','Daylight GNU/Linux'),('og:title',title),('og:description',description),('og:url',canonical),('og:locale','fr_CH' if lang=='fr' else 'en_GB'),('og:image',SITE+'/media/daylight-share.jpg'),('og:image:width','1200'),('og:image:height','630'),('og:image:alt','Daylight GNU/Linux — Raspberry Pi first')]:
                metadata+='<meta property="'+prop+'" content="'+esc(value,quote=True)+'">'
            metadata+='<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+esc(title,quote=True)+'"><meta name="twitter:description" content="'+esc(description,quote=True)+'"><meta name="twitter:image" content="'+SITE+'/media/daylight-share.jpg"><script type="application/ld+json">'+payload+'</script>'
            document='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title>'+metadata+'<link rel="icon" href="/assets/v5/daylight.svg" type="image/svg+xml"><link rel="stylesheet" href="'+assets['style.css']+'"><script src="'+assets['main.js']+'" defer></script></head><body><a class="skip" href="#main">'+T('Aller au contenu','Skip to content')+'</a>'+header+'<main id="main" tabindex="-1">'+body+'</main><div class="wrap"><p id="copy-status" class="status" role="status" aria-live="polite"></p></div>'+footer+'</body></html>'
            dest=out/(p.lstrip('/')+name);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(document)
            urls.append((canonical,name))
        feed_title=T('Daylight GNU/Linux — actualités','Daylight GNU/Linux — news')
        feed='<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>'+esc(feed_title)+'</title><link>'+SITE+p+'</link><description>'+esc(intro)+'</description><language>'+lang+'</language><atom:link href="'+SITE+L('feed.xml')+'" rel="self" type="application/rss+xml"/><item><title>'+T('Raspberry Pi au premier plan','Raspberry Pi takes the lead')+'</title><link>'+SITE+L('news.html')+'</link><guid isPermaLink="false">daylight-site-2026-11-02-'+lang+'</guid><pubDate>Mon, 02 Nov 2026 09:00:00 GMT</pubDate><description>'+esc(T('Un parcours Raspberry Pi, un menu mobile complet et de nouveaux guides pour découvrir et contribuer.','A Raspberry Pi pathway, complete mobile menu and new guides to discover and contribute.'))+'</description></item><item><title>Daylight GNU/Linux '+esc(version)+'</title><link>'+REPO+'/releases/tag/'+release['tag']+'</link><guid isPermaLink="true">'+REPO+'/releases/tag/'+release['tag']+'</guid><description>'+esc(rc_note)+'</description></item></channel></rss>'
        (out/(p.lstrip('/')+'feed.xml')).write_text(feed)
    # The media pack is intentionally factual and includes no third-party fonts.
    readme='Daylight GNU/Linux — Media kit\n\nFounder and developer: Hamdy Abou El Anein\nContact: '+EMAIL+'\nPrimary target: Raspberry Pi OS 64-bit (ARM64).\nThe AMD64 PC live image is a way to discover and test the desktop.\nPublished version: '+version+' (release candidate).\nWebsite: '+SITE+'\nSource: '+REPO+'\n\nKeep attribution. Daylight source and logo: GPL-3.0-only.\nScreenshots show the published PC/VM live environment, not Pi performance measurements.\nArtwork provenance and third-party rights are detailed in CREDITS.txt.\nNo font files are distributed. No invented user counts, ratings or speedup claims.\n'
    with zipfile.ZipFile(out/'media/daylight-media-kit.zip','w',zipfile.ZIP_DEFLATED) as pack:
        pack.writestr('README.txt',readme)
        pack.write(ROOT/'LICENSE','LICENSE-GPL-3.txt')
        pack.write(ROOT/'assets/branding/daylight.svg','daylight.svg')
        pack.write(out/'media/CREDITS.txt','CREDITS.txt')
        pack.write(out/'media/daylight-share.jpg','daylight-share.jpg')
        for name,*_ in shots:pack.write(out/'media'/name,'screenshots/'+name)
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(url)+'</loc></url>' for url,_ in urls)+'</urlset>')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE+'/sitemap.xml\n')
    print('Discovery pages:',len(urls),'languages: EN/FR; complete no-JS navigation; screenshots:',len(shots))
