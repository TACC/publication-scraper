import json
import logging
import csv
import os

import click
from click_loglevel import LogLevel

from version import __version__
import config

from APIClasses.PubMed import PubMed
from APIClasses.arXiv import ArXiv
from APIClasses.MDPI import MDPI
from APIClasses.Elsevier import Elsevier
from APIClasses.Springer import Springer
from APIClasses.Wiley import Wiley
from APIClasses.CrossRef import CrossRef

LOG_FORMAT = config.LOGGER_FORMAT_STRING
LOG_LEVEL = config.LOGGER_LEVEL
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger()


def set_logging_level(ctx, param, value):
    """
    Callback function for click that sets the logging level
    """
    logger.setLevel(value)
    return value


def set_log_file(ctx, param, value):
    """
    Callback function for click that sets a log file
    """
    if value:
        fileHandler = logging.FileHandler(value, mode="w")
        logFormatter = logging.Formatter(LOG_FORMAT)
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)
    return value


@click.command()
@click.version_option(__version__)
@click.option(
    "--log-level",
    type=LogLevel(),
    default=logging.INFO,
    is_eager=True,
    callback=set_logging_level,
    help="Set the log level",
    show_default=True,
)
@click.option(
    "--log-file",
    type=click.Path(writable=True),
    is_eager=True,
    callback=set_log_file,
    help="Set the log file",
)
@click.option(
    "-i", "--input_file", type=str, default="input.csv", help="Specify input file"
)
@click.option("-o", "--output_file", default="output.json", help="Specify output file")
@click.option(
    "-n",
    "--number",
    type=int,
    default=10,
    help="Specify max number of publications to receive for each author",
)
@click.option(
    "--apis",
    "-a",
    type=click.Choice(
        ["PubMed", "ArXiv", "MDPI", "Elsevier", "Springer", "Wiley", "CrossRef"],
        case_sensitive=False,
    ),
    multiple=True,
    default=["PubMed", "ArXiv", "MDPI", "Elsevier", "Springer", "Wiley", "CrossRef"],
    show_default=True,
    help="Specify APIs to query",
)
# TODO: I don't like the help message saying 'available' for querying, rephrase for clarity
@click.option(
    "--list",
    "list_apis",
    is_flag=True,
    default=False,
    help="List APIs available for querying",
)
# TODO: batch author names to circumvent rate limits?
def main(log_level, log_file, input_file, number, output_file, apis, list_apis):
    logger.debug(f"Logging is set to level {logging.getLevelName(log_level)}")
    if log_file:
        logger.debug(f"Writing logs to {log_file}")

    if list_apis:
        click.echo(
            "Available endpoints:\n  Pubmed\n  ArXiv\n  MDPI\n  Elsevier\n  Springer\n  Wiley\n  CrossRef"
        )
        return 0

    author_names = []
    try:
        with open(input_file, newline="") as csvfile:
            name_reader = csv.reader(csvfile)
            for row in name_reader:
                author_names.append(row[0])
    except FileNotFoundError:
        logger.error(f"Couldn't read input file {input_file}, exiting")
        exit(1)

    logger.debug(f"Querying the following APIs: {apis}")
    logger.debug(f"Requesting {number} publications for each author")

    available_apis = {
        "PubMed": PubMed(),
        "ArXiv": ArXiv(),
        "MDPI": MDPI(),
        "Elsevier": Elsevier(),
        "Springer": Springer(),
        "Wiley": Wiley(),
        "CrossRef": CrossRef(),
    }
    authors_and_pubs = []

    for author in author_names:
        results = {author: []}
        # FIXME: these names are too similar and confusing
        authors_pubs = []
        for api_name in apis:
            api = available_apis[api_name]
            # api = class_name()
            pubs_found = api.get_publications_by_author(author, number)
            if pubs_found is not None:
                authors_pubs += pubs_found

            results.update({author: authors_pubs})

        authors_and_pubs.append(results)

    logger.info(f"Found publications for {len(authors_and_pubs)} authors")

    # NOTE: main.py currently writes output to a JSON file. it will eventually return a TabLib
    # object and the final output will be user-configurable through the command line
    logger.debug(f"Results: {(json.dumps(authors_and_pubs, indent=2))}")

    logger.debug(f"Writing results to {output_file}")
    try:
        os.remove(output_file)
        logger.debug(f"successfully removed {output_file}")
    except Exception:
        logger.warning(f"could not remove {output_file}")

    fout = open(output_file, "w")
    fout.write(json.dumps(authors_and_pubs, indent=2))
    logger.info(f"wrote results to {output_file}")
    return 0


if __name__ == "__main__":
    main()
