"""Console script for vmdcli."""
import json
import logging
import os, sys
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


@click.command()
@click.option(
    '--verbose',
    default=False,
    is_flag=True)
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
def main(verbose: bool, days:str, dept:str, pbtoken: str):
    """Look for available appointment(s) in the next X days in your departement.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    logger.info(f"Looking for available appointements in departement {dept} in the next {days} days...")
    r = requests.get(f"{BASE_URL}/{dept}.json")
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
        as_for_period = int(centre.get('appointment_schedules', {}).get(f'{days}_days'))
        if as_for_period > 0:
            logger.info(f"{centre['nom']}: {as_for_period} available appointements in the next {days} days")
            logger.info(f"  > {centre['url']}")
            logger.info(f"  > Vaccins proposés: {','.join(centre.get('vaccine_type', []))}")
            logger.info(f"  > Type d'établissement: {centre.get('type')}")
            logger.debug(f"  > Metadata: {json.dumps(centre.get('metadata'), indent=4)}")
            if pbtoken:
                pb = Pushbullet(pbtoken)
                pb.push_link(
                    f"{centre['nom']}: {as_for_period} available appointements in the next {days} days",
                    centre['url']
                )
                logger.debug("Pushbullet notification sent")
        else:
            logger.debug(f"{centre['nom']}: no available appointment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
