Publication Scraper for UTRC Reports
====================================

This tool is designed to pull publication information associated with a given
author, institution, and date range.

## Prerequisites
- Git
- Docker
---
## Installation
```console
> git clone git@github.com:tacc/publication-scraper.git
> cd publication-scraper
> bash run.sh
```
**NOTE: You must first create a `.env` file containing your API keys for each endpoint! See [.env.sample](https://github.com/TACC/publication-scraper/blob/development/.env.sample) for example config.**
## Usage
Execute the script with `run.sh`, which will automatically build the `pubscraper` Docker container (if required) and run the main work script inside the container.
```console
> bash run.sh
Usage: pubscraper [OPTIONS]

Options:
  --version                       Show the version and exit.
  --log-level [NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set the log level  [default: 20]
  --log-file PATH                 Set the log file
  -i, --input_file TEXT           Specify input file
  -o, --output_file TEXT          Specify output file
  -n, --number INTEGER            Specify max number of publications to receive
                                  for each author
  -a, --apis [PubMed|ArXiv|MDPI|Elsevier|Springer|Wiley|CrossRef|PLOS]
                                  Specify APIs to query  [default: PubMed,
                                  ArXiv, MDPI, Elsevier, Springer, Wiley,
                                  CrossRef, PLOS]
  --list                          List APIs available for querying
  -f, --format [json|csv|xlsx]    Select the output format from: csv, xlsx, or
                                  json.  [default: json]
  -cd, --cutoff_date TEXT         Specify the latest date to pull publications.
                                  Example input: 2024 or 2024-05 or 2024-05-10.
  --help                          Show this message and exit.
```
To run the scraper with the default options (using the included sample input), invoke the `pubscraper` command:
```console
> bash run.sh pubscraper
```
By default, the script will request 10 publications from each API for each author, writing the results to `output.json`.

The tool expects an Excel spreadsheet as input, appearing as follows:
root_institution_name| first_name| last_name|...
---|---|---|---
The University of Texas| James| Carson| ...
The University of Texas| Kelsey| Beavers| ...

#### Output format can be specified with the `--format` or `-f` flag

Json output file (default format is json)
```console
> bash run.sh pubscraper -f json
> bash run.sh pubscraper --format json
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
> bash run.sh pubscraper -f csv
> bash run.sh pubscraper --format csv
```

```console
output.csv

From,Author,DOI,Journal,Content Type,Publication Date,Title,Authors
PubMed,James Carson,10.1186/s12889-024-20291-5,BMC Public Health,N/A,2024/10/22 00:00,Social inequalities in child mental health trajectories: a longitudinal study using birth cohort data 12 countries,"Cadman T,Avraam D,Carson J,Elhakeem A,Grote V,Guerlich K,Guxens M,Howe LD,Huang RC,Harris JR,Houweling TA,Hyde E,Jaddoe V,Jansen PW,Julvez J,Koletzko B,Lin A,Margetaki K,Melchior M,Nader JT,Pedersen M,Pizzi C,Roumeliotaki T,Swertz M,Tafflet M,Taylor-Robinson D,Wootton RE,Strandberg-Larsen K"
PubMed,James Carson,10.1002/cnm.3559,International Journal for Numerical Methods in Biomedical Engineering,N/A,2021/12/27 00:00,Automating fractional flow reserve (FFR) calculation from CT scans: A rapid workflow using unsupervised learning and computational fluid dynamics,"Chakshu NK,Carson JM,Sazonov I,Nithiarasu P"
Elsevier,Kelsey Beavers,10.1016/j.jcis.2015.10.053,Journal of Colloid and Interface Science,Article,2016-02-01,High conversion of HAuCl<inf>4</inf> into gold nanorods: A re-seeding approach,Canonico-May S.A.
Springer,Kelsey Beavers,10.1186/s12874-024-02252-z,BMC Medical Research Methodology,Article,2024-06-03,Use of systems thinking and adapted group model building methods to understand patterns of technology use among older adults with type 1 diabetes: a preliminary process evaluation,"Kahkoska, Anna R., Smith, Cambray, Young, Laura A., Hassmiller Lich, Kristen"
...
```


XLSX output file 
```console
> bash run.sh pubscraper -f xlsx
> bash run.sh pubscraper --format xlsx
```

```console
output.xlsx

From	Author	DOI	Journal	Content Type	Publication Date	Title	Authors
PubMed	Dan Stanzione	10.1038/s41592-024-02296-5	Nature Methods	N/A	2024-05-07	Author Correction: brainlife.io: a decentralized and open-source cloud platform to support neuroscience research	Hayashi S,Caron BA,Heinsfeld AS,Vinci-Booher S,McPherson B,Bullock DN,Bertò G,Niso G,Hanekamp S,Levitas D,Ray K,MacKenzie A,Avesani P,Kitchell L,Leong JK,Nascimento-Silva F,Koudoro S,Willis H,Jolly JK,Pisner D,Zuidema TR,Kurzawski JW,Mikellidou K,Bussalb A,Chaumon M,George N,Rorden C,Victory C,Bhatia D,Aydogan DB,Yeh FC,Delogu F,Guaje J,Veraart J,Fischer J,Faskowitz J,Fabrega R,Hunt D,McKee S,Brown ST,Heyman S,Iacovella V,Mejia AF,Marinazzo D,Craddock RC,Olivetti E,Hanson JL,Garyfallidis E,Stanzione D,Carson J,Henschel R,Hancock DY,Stewart CA,Schnyer D,Eke DO,Poldrack RA,Bollmann S,Stewart A,Bridge H,Sani I,Freiwald WA,Puce A,Port NL,Pestilli F
PubMed	Dan Stanzione	10.1038/s41592-024-02237-2	Nature Methods	N/A	2024-04-11	brainlife.io: a decentralized and open-source cloud platform to support neuroscience research	Hayashi S,Caron BA,Heinsfeld AS,Vinci-Booher S,McPherson B,Bullock DN,Bertò G,Niso G,Hanekamp S,Levitas D,Ray K,MacKenzie A,Avesani P,Kitchell L,Leong JK,Nascimento-Silva F,Koudoro S,Willis H,Jolly JK,Pisner D,Zuidema TR,Kurzawski JW,Mikellidou K,Bussalb A,Chaumon M,George N,Rorden C,Victory C,Bhatia D,Aydogan DB,Yeh FC,Delogu F,Guaje J,Veraart J,Fischer J,Faskowitz J,Fabrega R,Hunt D,McKee S,Brown ST,Heyman S,Iacovella V,Mejia AF,Marinazzo D,Craddock RC,Olivetti E,Hanson JL,Garyfallidis E,Stanzione D,Carson J,Henschel R,Hancock DY,Stewart CA,Schnyer D,Eke DO,Poldrack RA,Bollmann S,Stewart A,Bridge H,Sani I,Freiwald WA,Puce A,Port NL,Pestilli F
PubMed	Dan Stanzione	10.1371/journal.pcbi.1011270	PLOS Computational Biology	N/A	2024-02-07	CyVerse: Cyberinfrastructure for open science	Swetnam TL,Antin PB,Bartelme R,Bucksch A,Camhy D,Chism G,Choi I,Cooksey AM,Cosi M,Cowen C,Culshaw-Maurer M,Davey R,Davey S,Devisetty U,Edgin T,Edmonds A,Fedorov D,Frady J,Fonner J,Gillan JK,Hossain I,Joyce B,Lang K,Lee T,Littin S,McEwen I,Merchant N,Micklos D,Nelson A,Ramsey A,Roberts S,Sarando P,Skidmore E,Song J,Sprinkle MM,Srinivasan S,Stanzione D,Strootman JD,Stryeck S,Tuteja R,Vaughn M,Wali M,Wall M,Walls R,Wang L,Wickizer T,Williams J,Wregglesworth J,Lyons E
PubMed	Dan Stanzione		ArXiv	N/A	2023-08-11	brainlife.io: A decentralized and open source cloud platform to support neuroscience research	Hayashi S,Caron BA,Heinsfeld AS,Vinci-Booher S,McPherson B,Bullock DN,Bertò G,Niso G,Hanekamp S,Levitas D,Ray K,MacKenzie A,Kitchell L,Leong JK,Nascimento-Silva F,Koudoro S,Willis H,Jolly JK,Pisner D,Zuidema TR,Kurzawski JW,Mikellidou K,Bussalb A,Rorden C,Victory C,Bhatia D,Baran Aydogan D,Yeh FC,Delogu F,Guaje J,Veraart J,Bollman S,Stewart A,Fischer J,Faskowitz J,Chaumon M,Fabrega R,Hunt D,McKee S,Brown ST,Heyman S,Iacovella V,Mejia AF,Marinazzo D,Craddock RC,Olivetti E,Hanson JL,Avesani P,Garyfallidis E,Stanzione D,Carson J,Henschel R,Hancock DY,Stewart CA,Schnyer D,Eke DO,Poldrack RA,George N,Bridge H,Sani I,Freiwald WA,Puce A,Port NL,Pestilli F
...
```

#### Output format can be specified with the `--cutoff_date` or `-cd` flag

Adding `--cutoff_date` or `-cd` to command options will specify the latest date to pull publications. 
It can automatically recognize and parse various date formats such as YYYY-MM-DD, YYYY-MM, YYYY.

* For a publication with a date of "2024-05-10", it will be parsed as datetime(2024, 5, 10).
* For a publication with a date of "2024-05", it will be parsed as datetime(2024, 5, 1), with the day defaulting to 1.
* For a publication with a date of "2024", it will be parsed as datetime(2024, 1, 1), with the month and day defaulting to 1.

Cutoff date output file 

```console
> bash run.sh pubscraper -f csv -cd 2024-05
```

```console
output.csv

From,Author,DOI,Journal,Content Type,Publication Date,Title,Authors
PubMed,Dan Stanzione,10.1038/s41592-024-02296-5,Nature Methods,N/A,2024-05-07,Author Correction: brainlife.io: a decentralized and open-source cloud platform to support neuroscience research,"Hayashi S,Caron BA,Heinsfeld AS,Vinci-Booher S,McPherson B,Bullock DN,Bertò G,Niso G,Hanekamp S,Levitas D,Ray K,MacKenzie A,Avesani P,Kitchell L,Leong JK,Nascimento-Silva F,Koudoro S,Willis H,Jolly JK,Pisner D,Zuidema TR,Kurzawski JW,Mikellidou K,Bussalb A,Chaumon M,George N,Rorden C,Victory C,Bhatia D,Aydogan DB,Yeh FC,Delogu F,Guaje J,Veraart J,Fischer J,Faskowitz J,Fabrega R,Hunt D,McKee S,Brown ST,Heyman S,Iacovella V,Mejia AF,Marinazzo D,Craddock RC,Olivetti E,Hanson JL,Garyfallidis E,Stanzione D,Carson J,Henschel R,Hancock DY,Stewart CA,Schnyer D,Eke DO,Poldrack RA,Bollmann S,Stewart A,Bridge H,Sani I,Freiwald WA,Puce A,Port NL,Pestilli F"
Springer,Dan Stanzione,10.1007/s00784-024-05968-w,Clinical Oral Investigations,Article,2024-10-07,Performance of large language artificial intelligence models on solving restorative dentistry and endodontics student assessments,"Künzle, Paul, Paris, Sebastian"
Springer,Dan Stanzione,10.1007/s00395-024-01072-y,Basic Research in Cardiology,Article,2024-10-01,β3-Adrenergic receptor overexpression in cardiomyocytes preconditions mitochondria to withstand ischemia–reperfusion injury,"Fernández-Tocino, Miguel, Pun-Garcia, Andrés, Gómez, Mónica, Clemente-Moragón, Agustín, Oliver, Eduardo, Villena-Gutierrez, Rocío, Trigo-Anca, Sofía, Díaz-Guerra, Anabel, Sanz-Rosa, David, Prados, Belén, Campo, Lara, Andrés, Vicente, Fuster, Valentín, Pompa, José Luis, Cádiz, Laura, Ibañez, Borja"
Springer,Dan Stanzione,10.1007/s44290-024-00034-6,Discover Civil Engineering,Article,2024-08-05,Geophysical and geoenvironmental engineering assessment of contaminated workstation soils in a metamorphic environment,"Ale, Temitayo Olamide, Ale, Taiwo Ayomide, Faseki, Oluyemi Emmanuel, Ajidahun, Johnson, Oluyinka, Ololade Toyin"
```

## Development
### Development Prerequisites
- Python >=3.12
- Poetry (using [asdf-poetry](https://github.com/asdf-community/asdf-poetry) is recommended)
- poetry-bumpversion plugin
  ```console
  > poetry self add poetry-bumpversion
  ```

Before developing, first install the script with developmend dependencies:
```console
poetry install --with dev
```
Invoke the script with poetry to run during development:
```console
poetry run pubscraper
```

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
