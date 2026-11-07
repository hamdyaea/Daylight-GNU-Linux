# Daylight GNU/Linux 5

**Un bureau léger, une identité solaire, une installation qui respecte le système existant.**

Fondateur et développeur : **Hamdy Abou El Anein** · Contact : **info@daylightlinux.ch** · Code Daylight : **GNU GPL v3**

[Site en français](https://daylightlinux.ch/fr/) · [Téléchargements](https://daylightlinux.ch/fr/download.html) · [Installation](https://daylightlinux.ch/fr/install.html) · [Essai dans le navigateur](https://daylightlinux.ch/fr/try-online.html) · [Livres](https://daylightlinux.ch/fr/books.html) · [Old](https://daylightlinux.ch/fr/old/) · [English](README.md)

## Raspberry Pi en priorité

Le projet vise d’abord une utilisation sur Raspberry Pi OS 64 bits. L’ISO AMD64 est un live pour découvrir et tester le bureau sur PC, pas une image à écrire sur la carte SD du Pi.

[Commencer sur Raspberry Pi](https://daylightlinux.ch/fr/raspberry-pi.html) · [FAQ](https://daylightlinux.ch/fr/faq.html) · [Communauté](https://daylightlinux.ch/fr/community.html)

## Deux façons de découvrir Daylight

**Paquets Debian :** un cœur Rust ARM64 ou AMD64, des thèmes, une session Fluxbox indépendante et des applications facultatives, sur Debian 12/13 ou une installation compatible de Raspberry Pi OS 64 bits.

**Image live PC :** une ISO Debian 13 AMD64 construite depuis une base propre avec ces mêmes paquets. Pas de copie d'un ordinateur personnel, pas de serveur SSH actif, pas de télémétrie, pas d'installateur sur disque ni de persistance par défaut. La version réellement publiée est indiquée sur la page Téléchargements et dans `release/current.json` ; une branche de développement ne constitue pas une publication.

La série **5.0.0-rc** reste une version candidate. Les essais virtuels ne constituent pas une certification de chaque matériel physique.

## Installer depuis le dépôt APT signé

Télécharger et inspecter le script, puis afficher son plan :

```sh
curl --fail --show-error --silent --proto '=https' \
  https://daylightlinux.ch/daylight-install.sh -o daylight-install.sh
less daylight-install.sh
sh daylight-install.sh --plan
```

Installation minimale, sans bureau :

```sh
sudo sh daylight-install.sh --core --yes
daylight status
daylight info
daylight doctor
```

Pour ajouter le bureau, utiliser `--desktop --yes`. Les jeux nécessitent `--desktop --games --yes`. Le profil `--repo-only --yes` configure uniquement le dépôt. Sans `--yes`, le script n'effectue aucun changement.

Le dépôt **https://daylightlinux.ch/apt/** utilise une clé dédiée, des métadonnées signées et une priorité limitée aux paquets Daylight. Empreinte publique :

```text
B057 5F82 1A31 DD20 753D E07C 50D2 1240 F4BC B02E
```

Les installations Daylight ne déclenchent ni mise à niveau globale du système, ni redémarrage, ni activation de télémétrie. Ces paquets sont destinés à Debian/Raspberry Pi OS, **pas à Manjaro/Arch**. Lire le [guide détaillé](docs/INSTALL.md), en particulier sur un serveur productif.

## Bureau, terminal et applications

Fluxbox conserve une session séparée ; Conky propose des profils sobres ; le terminal affiche le logo ASCII et les informations du système avec Fastfetch, ou avec son affichage de secours. Aucun appel Internet n'est effectué à l'ouverture du terminal. Les fenêtres natives utilisent YAD uniquement pendant leur utilisation : pas d'Electron ni de service permanent de réglages.

Les utilitaires et jeux partagent un programme Rust : mots de passe, températures, différences entre dates, état réseau local, alarme, intégration de synthèse vocale et jeux facultatifs. **Conky est configuré et optimisé, pas réécrit en Rust.**

```sh
daylight control-center
daylight monitor
daylight password 24
daylight update --dry-run
sudo daylight update
daylight remove --dry-run
sudo daylight remove
```

Les opérations APT demandent confirmation. La suppression ne lance jamais autoremove, ne remplace pas les fichiers personnels préexistants et conserve les dépendances partagées ainsi que les réglages utilisateur. Ce n'est pas une restauration bit à bit par snapshot. Aucun nouveau gestionnaire de connexion n'est installé automatiquement.

## Paysages signés Daylight Linux

Le fond alpin approuvé, sa variante sombre et le fond de terminal utilisent une scène photoréaliste générée, à sa résolution livrée de **1672 × 941**. Deux photographies de montagne CC0 complètent la collection en **3840 × 2160**. Les paysages portent la signature **Daylight Linux**, conservée dans le cadrage sur différents formats d'écran.

Les crédits distinguent explicitement les scènes générées des photographies réelles. Les sources et leurs empreintes sont documentées ; aucune résolution agrandie n'est vendue comme de la 4K native. Aucun fichier de police autonome n'est redistribué. [Fonds d'écran](https://daylightlinux.ch/fr/wallpapers.html) · [Provenance](docs/ARTWORK.md)

## Essai web sans charger le serveur du projet

**Aperçu léger en un clic :** [Daylight Web](https://daylightlinux.ch/live/?lang=fr) démarre un véritable Linux Alpine x86 avec Fluxbox directement dans le navigateur, grâce à v86/WebAssembly. Sans compte ni installation : environ 42 Mo au premier lancement et 256 Mio de RAM pour le système invité, plus la mémoire du navigateur. Aucun relais réseau externe ni stockage persistant. Il s'agit explicitement d'un aperçu expérimental Alpine, pas de la version complète Debian/Raspberry Pi OS. [Construction, tests et sources](web-live/README.md)

**Édition live Debian complète :**

`demo/` fournit un environnement privé QEMU/noVNC utilisant la véritable ISO, pas une imitation HTML. La configuration Codespaces est disponible depuis la page d'essai. **Aucune machine virtuelle visiteur ne fonctionne sur le Raspberry Pi hébergeant le site.**

Le compte et le quota Codespaces du visiteur sont utilisés ; des frais peuvent s'appliquer. Le système invité n'a ni réseau, ni disque hôte, ni persistance ; sa durée est limitée. Il faut arrêter/supprimer le Codespace séparément après utilisation. Ce n'est pas un service anonyme public multi-utilisateur. L'inscription sur DistroSea dépend de son opérateur et n'est pas présentée comme effectuée. [Détails et limites](demo/README.md)

## Tests, confidentialité et maintenance

Le pipeline vérifie le Rust, les commandes, le collecteur, les signatures APT, les ressources, le cycle d'installation/suppression et les fenêtres natives sous Debian 12/13. Il teste également le démarrage du système live, les véritables chargeurs BIOS/UEFI et la connexion du navigateur au bureau effectivement prêt. Les résultats, révisions exactes et limites sont conservés dans [la validation RC2](docs/VALIDATION-RC2.md) et les archives de chaque publication.

Le compteur de démarrages est optionnel, désactivé et non installé par le bootstrap. Son serveur n'est pas activé en production. Il compte des démarrages reçus, **pas des utilisateurs uniques** ; l'adresse IP reste visible au niveau transport. Voir [Confidentialité](docs/PRIVACY.md).

Les textes, configurations et signatures actuels utilisent `info@daylightlinux.ch`. La livraison effective du courrier n'est pas certifiée par un build ; les issues GitHub restent disponibles. Les publications historiques immuables conservent leurs métadonnées d'origine.

[Construction](docs/BUILD.md) · [Exploitation du dépôt et du site](docs/OPERATIONS.md) · [Sécurité du serveur productif](docs/PRODUCTION-SAFETY.md) · [Anciennes versions](https://daylightlinux.ch/fr/old/)
