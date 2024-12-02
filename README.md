Publication Scraper for UTRC Reports
====================================

This tool is designed to pull publication information associated with a given
author, institution, and date range.

## Prerequisites
- Git
- Python >=3.12
- Poetry (using [asdf-poetry](https://github.com/asdf-community/asdf-poetry) is recommended)
- poetry-bumpversion plugin
  ```console
  > poetry self add poetry-bumpversion
  ```
---
## Installation
```console
> git clone git@github.com:tacc/publication-scraper.git
> cd publication-scraper
> poetry install
```
## Usage
**NOTE: you must first create a `secrets.json` containing your API keys for each endpoint! See [secrets.sample](https://github.com/TACC/publication-scraper/blob/cli_additions/secrets.sample) for example config.**

By default, author names are read in from `input.csv` and API results are written to `output.json`.
```console
> poetry run pubscraper --help
Usage: pubscraper [OPTIONS]

Options:
  --version                       Show the version and exit.
  --log-level [NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level  [default: 20]
  --log-file PATH                 Set the log file
  -i, --input_file TEXT           Specify input file
  -o, --output_file TEXT          Specify output file
  -n, --number INTEGER            Specify max number of publications to
                                  receive for each author
  -a, --apis [PubMed|ArXiv|MDPI|Elsevier|Springer|Wiley|CrossRef]
                                  [default: PubMed, ArXiv, MDPI, Elsevier,
                                  Springer, Wiley, CrossRef]
  --help                          Show this message and exit.
```
## Development
To update the version, use the `poetry version <major|minor|patch>` command (aided by the poetry-bumpversion plugin):
```console
> poetry version patch
Bumping version from 0.1.0 to 0.1.1
poetry_bumpversion: processed file pubscraper/version.py
```
This will update the version in both the `pyproject.toml` and the `pubscraper/version.py` files. If you want to first test the version bump, you can use the `--dry-run` flag:
```console
poetry version patch --dry-run
Bumping version from 0.1.0 to 0.1.1
poetry_bumpversion: processed file pubscraper/version.py
```
After updating the version and committing the changes back to the repo, you should `tag` the repo to match this version:
```console
git tag -a 0.1.1 -m "Version 0.1.1"
git push origin 0.1.1
```
