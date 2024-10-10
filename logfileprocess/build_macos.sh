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
# 这个命令会创建一个Xcode项目
briefcase build macos xcode

# 打包成release
# briefcase package android
#Compile

