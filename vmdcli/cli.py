"""Console script for vmdcli."""

import json
import logging
import os, sys
from time import sleep
from datetime import datetime
import click
import requests
from pytz import timezone
import humanize
from pushbullet import Pushbullet

BASE_URL="https://vitemadose.gitlab.io/vitemadose"
AVAILABLE_DAYS_CHOICES = ["1", "2", "7", "28", "49"]
TZ = "Europe/Paris"

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING) # A bit too verbose
logging.getLogger("urllib3").setLevel(logging.WARNING)  # A bit too verbose

# Look for current module version
try:
    vmdcli_version = sys.modules['vmdcli'].__version__
except KeyError:
    from _version import __version__ as vmdcli_version
headers = { 
    'User-Agent': f'vitemadose-cli v{vmdcli_version}',
}

@click.command()
@click.option(
    '-v',
    '--verbose',
    help='Enable verbose mode',
    default=False,
    is_flag=True)
@click.option(
    '-q',
    '--quiet',
    help='Quiet mode',
    default=False,
    is_flag=True)
@click.option(
    '-c',
    '--chrono',
    help='Only look for "chronodoses"',
    default=False,
    is_flag=True)
@click.option(
    '-s',
    '--watch',
    help='Watch mode, sleep X seconds before replaying',
    type=int,
    required=False)
@click.option(
    '--days',
    help='Number of days to look at for available appointment(s)',
    type=click.Choice(AVAILABLE_DAYS_CHOICES),
    default="2")
@click.option(
    '--dept',
    prompt='Your departement',
    help='Your departement number')
@click.option(
    '--pbtoken',
    help='Pushbullet token to send a notification',
    required=False)
def main(verbose: bool, quiet: bool, chrono: bool, watch:int, days:str, dept:str, pbtoken: str):
    """Look for available appointment(s) in the next X days in your departement.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    if quiet:
        logger.setLevel(logging.CRITICAL)
    if not chrono:
        logger.info(f"Looking for available appointements in departement {dept} in the next {days} days...")
        _looking_period = f'{days}_days'
    else:
        logger.info(f"Looking for available appointements in departement {dept} for 'chronodoses'")
        _looking_period = 'chronodose'
    last_notifications = []
    while True:
        new_last_notifications = []
        r = requests.get(f"{BASE_URL}/{dept}.json", headers=headers)
        if r.status_code == 404:
            # Easy one to understand
            logger.error("Invalid departement number")
            sys.exit(-1)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
            # If not raise: juste leave in error
            logger.error(f"Unable to process response with status code {r.status_code}")
            sys.exit(-1)
        try:
            data = r.json()
        except json.JSONDecodeError:
            logger.error("Invalid json data")
            sys.exit(-1)

        last_update = datetime.fromisoformat(data.get('last_updated'))
        delta = datetime.now(timezone(TZ))-last_update
        logger.info(f"Last data update: {humanize.naturaldelta(delta)}")
        for centre in data.get("centres_disponibles", []):
            for app_sch in centre.get('appointment_schedules', []):
                if app_sch.get('name') == _looking_period:
                    nb_slots = app_sch.get('total', 0)
                    if nb_slots > 0:
                        if not chrono:
                            _title = f"{centre['nom']}: {nb_slots} available appointements in the next {days} days"
                        else:
                            _title = f"{centre['nom']}: {nb_slots} 'chronodoses' availables"
                        logger.info(_title)
                        logger.info(f"  > {centre['url']}")
                        logger.info(f"  > Vaccins proposés: {','.join(centre.get('vaccine_type', []))}")
                        logger.info(f"  > Type d'établissement: {centre.get('type')}")
                        logger.debug(f"  > Metadata: {json.dumps(centre.get('metadata'), indent=4)}")
                        if pbtoken:
                            if (centre['nom'], nb_slots) not in last_notifications:
                                pb = Pushbullet(pbtoken)
                                pb.push_link(_title, centre['url'])
                                logger.debug("Pushbullet notification sent")
                            else:
                                logger.debug("Already notified")
                            new_last_notifications.append((centre['nom'], nb_slots))
            else:
                logger.debug(f"{centre['nom']}: no available appointment")
        if not watch:
            return 0
        else:
            if watch < 1:
                logger.warning("La période minimal de l'option watch est d'une seconde.")
                watch = 1
            sleep(watch)
            last_notifications = new_last_notifications
            print("\033c")
            logger.debug(f"Already notified: {last_notifications}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
