#!/bin/bash

set -ex

FILE_NAME=~/SPEEDDATA/speed-$(date +%s).json
speedtest-cli --single --json > ${FILE_NAME}
