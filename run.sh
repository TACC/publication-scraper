#!/bin/bash

set -euo pipefail

IMAGENAME="joeleehen/pubscraper"
IMAGEVERSION=${IMAGEVERSION:-latest}
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE_DOCKER=${FORCE_DOCKER:-0}

die() {
  echo "$!" 1>&2
  exit 1
}

realpath() {
  echo "$(
    cd "$(dirname "$1")"
    pwd
  )"
}

# should we run installed version or from docker image?
# check for installed version
DOCKER_RUN=""
# check for docker install
docker info >/dev/null || die "Docker is not installed. Exiting"

# check for image loaded
DOCKER_IMAGE=$(docker images -q "${IMAGENAME}:${IMAGEVERSION}")

# if not, build it
if [ -z "${DOCKER_IMAGE}" ]; then
  docker build -t "${IMAGENAME}:${IMAGEVERSION}" "${BUILD_DIR}"
fi

DOCKER_RUN="docker run -t --rm --env-file ${BUILD_DIR}/.env -v $(pwd):/publication-scraper ${IMAGENAME}:${IMAGEVERSION} "

echo "${DOCKER_RUN} $@" 1>&2
${DOCKER_RUN} "$@"
