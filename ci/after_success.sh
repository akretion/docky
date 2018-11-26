#!/bin/bash
set -e

echo "$TRAVIS_BRANCH"
echo "$TRAVIS_PULL_REQUEST"
echo "$TRAVIS_PYTHON_VERSION"

if [ "$TRAVIS_BRANCH" == "master" ] &&
   [ "$TRAVIS_PULL_REQUEST" == "false" ] &&
   [ "$TRAVIS_PYTHON_VERSION" == "3.6" ]; then
    echo "install building doc dependency"
    pip install -U -r requirements-docs.txt
    echo "start building doc"
    ./build_doc.py
fi
