coveralls

if ([ "$TRAVIS_BRANCH" == "master" ] || [ ! -z "$TRAVIS_TAG" ]) &&
    [ "$TRAVIS_PULL_REQUEST" == "false" ] &&
    [ "$TRAVIS_PYTHON_VERSION" == "3.6" ]; then
    pip install -U -r requirements-docs.txt
    ./build_doc.py
fi
