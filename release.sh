#!/bin/bash

TAG=$1;

git tag v${TAG} -m "Version ${TAG}"

python3 setup.py sdist bdist_wheel

twine upload dist/*