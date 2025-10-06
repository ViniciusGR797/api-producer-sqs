#!/bin/bash
set -e

bash infra/build-lambda.sh

bash infra/stack-setup.sh
