#!/bin/bash

TAG=$1
MSG="Version ${TAG}"

echo "Adding files to commit..."
git add .

echo "Creating commit ${MSG}..."
git commit -m "${MSG}"

echo "Tagging..."
git tag v${TAG} -m "${MSG}"

rm -rf dist/*

python3 setup.py sdist bdist_wheel

twine upload dist/*