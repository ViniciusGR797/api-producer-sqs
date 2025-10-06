#!/bin/bash
set -e

LAMBDA_NAME="api-producer-sqs"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  PROJECT_ROOT=$(pwd -W)
  BUILD_DIR="${PROJECT_ROOT}\\infra\\lambda_build"
else
  PROJECT_ROOT="$(pwd)"
  BUILD_DIR="${PROJECT_ROOT}/infra/lambda_build"
fi

ZIP_FILE="${BUILD_DIR}/${LAMBDA_NAME}.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

PROJECT_ROOT_DOCKER=$(echo "$PROJECT_ROOT" | sed 's#^C:#/c#' | sed 's#\\#/#g')
BUILD_DIR_DOCKER=$(echo "$BUILD_DIR" | sed 's#^C:#/c#' | sed 's#\\#/#g')

docker run --rm \
    -v "${PROJECT_ROOT_DOCKER}":/var/task \
    -v "${BUILD_DIR_DOCKER}":/var/build \
    ubuntu:22.04 \
    bash -c "\
        set -e && \
        apt-get update -qq && \
        apt-get install -y python3-pip zip >/dev/null && \
        pip3 install --upgrade pip >/dev/null && \
        pip3 install fastapi mangum uvicorn python-dotenv email-validator 'python-jose[cryptography]' boto3 autopep8 -t /var/build >/dev/null && \
        if [ -d /var/task/app ]; then cp -r /var/task/app/. /var/build/; fi && \
        cd /var/build && zip -r ${LAMBDA_NAME}.zip . >/dev/null \
    "

echo "Lambda zip created on: $ZIP_FILE"
