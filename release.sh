#!/bin/bash

TAG=$1;

git tag v${TAG} -m "Version ${TAG}"

rm -rf dist/*

python3 setup.py sdist bdist_wheel

twine upload dist/*