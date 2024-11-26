import json
import logging

import click
from click_loglevel import LogLevel

from version import __version__
import config
from APIClasses.PubMed import PubMed
from APIClasses.arXiv import ArxivAPI
from APIClasses.MDPI import MDPI

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
    "-n",
    "--number",
    type=int,
    default=10,
    help="Specify max number of publications to receive for each author",
)
def main(log_level, log_file, number):
    logger.debug(f"Logging is set to level {logging.getLevelName(log_level)}")
    if log_file:
        logger.debug(f"Writing logs to {log_file}")
    author_names = input("Enter author names(comma-separated): ").split(",")
    author_names = [name.strip() for name in author_names]

    logger.debug(f"Requesting {number} publications for each author")

    apis = [PubMed(), ArxivAPI(), MDPI()]
    authors_and_pubs = []

    for author in author_names:
        results = {author: []}
        # FIXME: these names are too similar and confusing
        authors_pubs = []
        for api in apis:
            pubs_found = api.get_publications_by_author(author, number)
            if pubs_found is not None:
                authors_pubs += pubs_found

            results.update({author: authors_pubs})

        authors_and_pubs.append(results)

    print(json.dumps(authors_and_pubs, indent=2))
    return authors_and_pubs


if __name__ == "__main__":
    main()