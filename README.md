# ViteMaDose - CLI

Ce projet est un petit outil en ligne de commande, permettant de détecter les rendez-vous disponibles dans votre 
département pour recevoir un vaccin contre la covid19.

Basé sur les données de [vitemadose.covidtracker.fr](https://vitemadose.covidtracker.fr/) (dont je tiens à féliciter 
l'équipe par la même occasion!), ce projet ne vise pas à s'y substituer: Les données les plus détaillées et les mieux
présentées sont accessibles via le site officiel, pas via cet outil.

Si un ou des rendez-vous sont disponibles, vous avez la possibilité de recevoir une notification sur votre téléphone,
via les services de [pushbullet.com](https://www.pushbullet.com/).

> **NDLR**: Pushbullet est assez simple à mettre en oeuvre et je l'utilisais déjà, d'où ce choix. Je ne doute pas que 
> d'autres systèmes feraient aussi bien voir mieux. N'hésitez pas à faire des PR!


> Le projet est en franglais car j'ai l'habitude de coder en Anglais mais la destination de ce projet est uniquement
> Française.

# Installation


```bash
pip install vmdcli
```

# Usage

```bash
vmd-cli --help

Usage: vmd.py [OPTIONS]

  Look for available appointment(s) in the next X days in your departement.

Options:
  --verbose
  --days [1|2|7|28|49]  Number of days to look at for available appointment(s)
  --dept TEXT           Your departement number
  --pbtoken TEXT        Pushbullet token to send a notification
  --help                Show this message and exit
```

## Example

```bash
vmd-cli --days 2 --dept 35
Looking for available appointements in departement 35 in the next 2 days...
Last data update: 2 minutes
Centre de vaccination COVID - Centre de vaccination du Naye - Vaccination Covid-19: 9 available appointements in the next 2 days
  > https://partners.doctolib.fr/centre-de-sante/saint-malo/centre-de-vaccination-covid-centre-de-vaccination-du-naye
  > Vaccins proposés: Pfizer-BioNTech
  > Type d'établissement: vaccination-center
```

# Notifications

Spécifiez un [Token d'API Pushbullet](https://docs.pushbullet.com/#api-quick-start) via l'argument `--pbtoken` pour 
recevoir une notification sur votre téléphone.

```bash
vmd-cli --days 2 --dept 35 --pbtoken "o.xxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

# Cron/Planification

Il est tout à fait possible de mettre la commande dans un gestionnaire de planification comme `cron`:

Par exemple pour recevoir une notification des centres de Gironde (33) avec des disponibilités dans les 2 jours à venir,
avec une vérification toutes les heures:

```
crontab -e

# Ajoutez:
# m h   dom mon dow   command
00  *   *   *   *     vmd-cli --days 2 --dept 35 --pbtoken "o.xxxxxxxxxxxxxxxxxxxxxxxxxxx"
```