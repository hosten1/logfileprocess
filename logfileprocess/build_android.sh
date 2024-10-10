#!/bin/bash

set -e

WORKSPACE=$(pwd)
echo $WORKSPACE

#Version
VERSION="3.2.14i."
echo $VERSION

#Get Date Time
CURRENT_DATE_TIME=$(date "+%Y%m%d%H%M.")
echo $CURRENT_DATE_TIME

#Get git commit id  newest
COMMITID="$(git rev-parse --short HEAD)"
echo $COMMITID

briefcase build android -r

# 打包成release
# briefcase package android
#Compile

