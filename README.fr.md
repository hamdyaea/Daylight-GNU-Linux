# Daylight GNU/Linux 5

**Un environnement léger et réversible pour Debian et Raspberry Pi OS.**

Fondateur et développeur : **Hamdy Abou El Anein**. Licence du code Daylight : **GNU GPL v3**. Contact du projet : **contact@daylightlinux.ch**, adresse en attente d'activation.

Cette version **5.0.0-rc.1** est une version candidate, pas une version déclarée stable. Consulter `docs/VALIDATION.md` pour distinguer les tests effectués des validations restantes.

## Ce qui est inclus

Une session Fluxbox indépendante, deux profils Conky, un terminal personnalisé avec Fastfetch facultatif et un affichage ASCII de secours, des thèmes montagne et soleil, ainsi que le fond d'écran historique. Les utilitaires et jeux sont regroupés autour d'un petit exécutable Rust ; les fenêtres natives utilisent YAD uniquement lorsqu'elles sont ouvertes. Pas d'Electron, de service permanent de réglages ni d'accès réseau à chaque ouverture du terminal.

Le programme fournit notamment `daylight status`, `daylight doctor`, `daylight info`, `daylight monitor`, `daylight password`, `daylight control-center`, `daylight update` et `daylight remove`. Les opérations APT proposent une simulation et demandent les droits nécessaires pour appliquer des changements.

## Installation

Les paquets ARM64 sont destinés aux systèmes Debian/Raspberry Pi OS 64 bits. Les paquets AMD64 sont destinés aux PC 64 bits. ARM 32 bits n'est pas encore pris en charge.

```sh
sudo apt install ./daylight-core_5.0.0~rc1_arm64.deb ./daylight-themes_5.0.0~rc1_all.deb
daylight status
daylight info
daylight remove --dry-run
```

Le bureau complet ajoute les paquets desktop, apps et linux. Les jeux et le compteur de démarrages restent optionnels. Lire `docs/INSTALL.md` avant l'installation, particulièrement sur un serveur productif.

Aucun gestionnaire de connexion n'est automatiquement installé ou redémarré. Les fichiers personnels `.bashrc`, `.fluxbox` et `.conkyrc` ne sont pas remplacés. Les réglages Daylight restent dans `~/.config/daylight`. La suppression ne lance jamais `apt autoremove` ; les dépendances et réglages personnels conservés ne constituent pas un retour bit à bit au système antérieur.

## Image live

La recette `live/` construit une ISO Debian 13 AMD64 avec les mêmes paquets. Elle ne copie pas un ordinateur personnel ni le Raspberry Pi productif. Les essais en machine virtuelle sont distingués des tests physiques et de la validation des chargeurs de démarrage. Aucun installateur sur disque, aucune persistance et aucune télémétrie active par défaut.

## Confidentialité et limites

Le compteur optionnel compte des **démarrages reçus**, pas des utilisateurs uniques. Il ne transmet pas d'identifiant persistant, de numéro de série, de MAC ou de nom d'utilisateur. L'adresse IP reste visible au niveau réseau : l'anonymat intégral du transport n'est pas promis. Le collecteur de référence n'est pas déployé automatiquement.

Le dépôt APT public, l'adresse Proton Mail et les réglages DNS ne sont pas considérés opérationnels sans validation séparée. Les thèmes vectoriels sont des propositions de travail ; ils ne sont pas présentés comme les wallpapers photoréalistes définitifs.

Documentation : `docs/BUILD.md`, `docs/INSTALL.md`, `docs/PRIVACY.md`, `docs/LEGACY-AUDIT.md`, `docs/PRODUCTION-SAFETY.md`, `docs/VALIDATION.md`.
