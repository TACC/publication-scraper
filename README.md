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

The the minimum command options required to run the program is shown below.
```console
> poetry run pubscraper -i input.csv
```

If -f or --format is not specified, the default format is json.

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
  -f, --format [json|csv]         Select the output format: csv or json.
                                  [default: json]
  --help                          Show this message and exit.
```

Examples of output file varied by format givin (-f or --format)

Json output file (default format is json)
```console
> poetry run pubscraper -i input.csv 
> poetry run pubscraper -i input.csv -f json
```

```console
output.json

[
    {
        "James Carson": [
            {
                "from": "PubMed",
                "journal": "BMC Public Health",
                "publication_date": "2024/10/22 00:00",
                "title": "Social inequalities in child mental health trajectories: a longitudinal study using birth cohort data 12 countries",
                "authors": "Cadman T,Avraam D,Carson J,Elhakeem A,Grote V,Guerlich K,Guxens M,Howe LD,Huang RC,Harris JR,Houweling TA,Hyde E,Jaddoe V,Jansen PW,Julvez J,Koletzko B,Lin A,Margetaki K,Melchior M,Nader JT,Pedersen M,Pizzi C,Roumeliotaki T,Swertz M,Tafflet M,Taylor-Robinson D,Wootton RE,Strandberg-Larsen K",
                "doi": "10.1186/s12889-024-20291-5"
            },
            ...

        ]
    }
     {
        "Kelsey Beavers": [
            {
                "from": "PubMed",
                "journal": "Proceedings of the Royal Society B: Biological Sciences",
                "publication_date": "2024/10/02 00:00",
                "title": "Trade-off between photosymbiosis and innate immunity influences cnidarian\u2019s response to pathogenic bacteria",
                "authors": "Emery MA,Beavers KM,Van Buren EW,Batiste R,Dimos B,Pellegrino MW,Mydlarz LD",
                "doi": "10.1098/rspb.2024.0428"
            },
            ...
        ]
    }
]
```


CSV output file 
```console
> poetry run pubscraper -i input.csv 
> poetry run pubscraper -i input.csv -f cvs
```

```console
output.cvs

Author,DOI,Journal,Publication Date,Title,Authors
James Carson,11515779,BMC Public Health,2024/10/22 00:00,Social inequalities in child mental health trajectories: a longitudinal study using birth cohort data 12 countries,"Cadman T,Avraam D,Carson J,Elhakeem A,Grote V,Guerlich K,Guxens M,Howe LD,Huang RC,Harris JR,Houweling TA,Hyde E,Jaddoe V,Jansen PW,Julvez J,Koletzko B,Lin A,Margetaki K,Melchior M,Nader JT,Pedersen M,Pizzi C,Roumeliotaki T,Swertz M,Tafflet M,Taylor-Robinson D,Wootton RE,Strandberg-Larsen K"
James Carson,11475381,International Journal for Numerical Methods in Biomedical Engineering,2021/12/27 00:00,Automating fractional flow reserve (FFR) calculation from CT scans: A rapid workflow using unsupervised learning and computational fluid dynamics,"Chakshu NK,Carson JM,Sazonov I,Nithiarasu P"
Kelsey Beavers,11444771,Proceedings of the Royal Society B: Biological Sciences,2024/10/02 00:00,Trade-off between photosymbiosis and innate immunity influences cnidarian’s response to pathogenic bacteria,"Emery MA,Beavers KM,Van Buren EW,Batiste R,Dimos B,Pellegrino MW,Mydlarz LD"
Kelsey Beavers,11579526,Integrative and Comparative Biology,2024/07/18 00:00,Structural and Evolutionary Relationships of Melanin Cascade Proteins in Cnidarian Innate Immunity,"Van Buren EW,Ponce IE,Beavers KM,Stokes A,Cornelio MN,Emery M,Mydlarz LD"
...
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
