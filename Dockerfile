FROM python:3.12-bookworm AS poetry
ENV POETRY_VERSION="1.8.4"

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /publication-scraper

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

COPY README.md LICENSE /publication-scraper
COPY pubscraper /publication-scraper/pubscraper

RUN ls
RUN poetry build


FROM python:3.12
LABEL maintainer="Joseph Hendrix <jlh7459@my.utexas.edu>"

# Update OS
RUN apt-get update && apt-get install -y \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure Python/Pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /publication-scraper

COPY --from=poetry /publication-scraper /publication-scraper/requirements.txt .

RUN pip install -r requirements.txt

COPY --from=poetry /publication-scraper/dist/*.whl ./

RUN pip install *.whl

COPY README.md LICENSE /pubscraper/

CMD [ "pubscraper", "--help" ]
