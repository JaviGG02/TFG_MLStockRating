#!/bin/bash

TARGET_DIRECTORY="./proto_app/backend/"
black $TARGET_DIRECTORY

echo "No black issues found in the Python code."
