# Daylight GNU/Linux 5

**Un environnement léger et réversible pour Debian et Raspberry Pi OS.**

Fondateur et développeur : **Hamdy Abou El Anein**. Licence du code Daylight : **GNU GPL v3**.

[Télécharger 5.0.0-rc.1](https://github.com/hamdyaea/Daylight-GNU-Linux/releases/tag/v5.0.0-rc.1) · [Installation](docs/INSTALL.md) · [Tests vérifiés](docs/VALIDATION.md) · [English](README.md)

## Une première version candidate publiée

**Daylight GNU/Linux 5.0.0-rc.1 est disponible** : huit fichiers `.deb`, une ISO live Debian 13 pour PC AMD64, les captures du bureau, les sommes SHA256 et les preuves de validation. Il s'agit d'une version candidate, pas d'une version stable certifiée sur tous les matériels.

L'ISO fait environ **1,27 Go**. Elle utilise les mêmes paquets et ne copie aucun ordinateur personnel. SSH et télémétrie sont désactivés ; aucun installateur sur disque ni persistance ne sont inclus.

![Capture réelle du bureau live](https://github.com/hamdyaea/Daylight-GNU-Linux/releases/download/v5.0.0-rc.1/daylight-live-desktop.png)

## Contenu

Une session Fluxbox distincte, deux profils Conky, un terminal personnalisé avec Fastfetch et un affichage ASCII de secours, des thèmes montagne et soleil et le fond d'écran historique. Les utilitaires et la logique des jeux utilisent un petit programme Rust ; les fenêtres natives utilisent YAD uniquement lorsqu'elles sont ouvertes. Aucun Electron ni service permanent de réglages.

Le programme fournit notamment `daylight status`, `daylight doctor`, `daylight info`, `daylight monitor`, `daylight password`, `daylight control-center`, `daylight update` et `daylight remove`. Conky est conservé et optimisé : il n'est pas présenté comme réécrit en Rust.

Sept types de paquets : `daylight-core`, `daylight-themes`, `daylight-desktop`, `daylight-apps`, `daylight-games`, `daylight-telemetry` et `daylight-linux`. Le core existe en ARM64 et AMD64 ; les six autres paquets sont indépendants de l'architecture.

## Installation minimale sur un Pi 64 bits

Après téléchargement des fichiers correspondants de la Release :

```sh
sudo apt install ./daylight-core_5.0.0.rc1_arm64.deb ./daylight-themes_5.0.0.rc1_all.deb
daylight status
daylight info
daylight remove --dry-run
```

Ces paquets sont destinés à Debian/Raspberry Pi OS, **pas à Manjaro**. Lire `docs/INSTALL.md` avant installation. GitHub remplace le caractère `~` par `.` dans les noms publiés ; la version Debian interne reste `5.0.0~rc1`. Les constructions locales conservent les noms avec `~`.

Aucun gestionnaire de connexion n'est démarré automatiquement. Les fichiers personnels `.bashrc`, `.fluxbox` et `.conkyrc` existants ne sont pas remplacés ; les réglages Daylight sont séparés. Fluxbox peut créer ses fichiers de compatibilité lorsqu'ils sont absents. La suppression ne lance pas `apt autoremove` et conserve les réglages personnels et dépendances partagées : ce n'est pas un retour bit à bit par snapshot.

## Validation réelle

Le commit candidat `85715705501b18138712173327b7df1fb63ef889` a passé la validation complète : **27 tests Rust, 11 tests CLI, 4 tests du collecteur, un test du dépôt APT signé**, puis installation, réinstallation et suppression sur Debian 12 et 13. **16 tests graphiques passent sur chacune des deux versions.**

L'ISO démarre hors réseau dans QEMU avec le compte live, Fluxbox et Conky. La capture ci-dessus provient de ce test. Les essais ARM64 ont aussi réussi sur le Raspberry Pi réel, par extraction du paquet sans installation du bureau ni interruption des services. Les détails sont dans `docs/VALIDATION.md`.

Le test live utilise le noyau et l'initrd extraits de l'ISO : il ne certifie pas les chargeurs BIOS/UEFI, Secure Boot, le Wi-Fi/audio physique ou une session graphique matérielle sur Pi.

## Confidentialité et travaux restants

Le compteur de démarrages est facultatif et désactivé par défaut. Il ne compte pas des utilisateurs uniques ; l'adresse IP reste visible au niveau réseau. Le collecteur de référence n'est pas déployé.

Le générateur de dépôt APT signé est développé et testé, mais le dépôt public n'est pas hébergé. `daylight update` a besoin d'une source configurée proposant de nouveaux paquets. Le contact **info@daylightlinux.ch reste à activer** ; utiliser les issues GitHub en attendant.

Les wallpapers vectoriels sont des propositions de travail, pas la collection photoréaliste définitive. ARM 32 bits, validation matérielle élargie et publication encyclopédique ne sont pas réalisés dans cette version candidate.

Les licences des composants tiers restent applicables. Les anciennes versions sont conservées dans `old/*` et leurs branches d'origine sont également préservées.
