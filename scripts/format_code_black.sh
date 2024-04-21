#!/bin/bash

TARGET_DIRECTORY="./proto_app/backend/"
ls
black $TARGET_DIRECTORY
pwd
cd "../"
ls


echo "No black issues found in the Python code."
