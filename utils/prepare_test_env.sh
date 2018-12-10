#!/bin/bash
set -o errexit
set -o xtrace

# Ensure you have the latest version of pip
pip install --upgrade pip

# Install packs requirements
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install the latest Tornado version that fulfills StackStorms
# requirements (>3.2) but does not fail due to Tornado's requirement
# of a python version with "an up-to-date SSL module"
# this means Tornado < 5.0.0
pip install tornado==4.5.3

# Checkout and install st2 requirements
git clone https://github.com/StackStorm/st2.git --depth 1 --single-branch --branch v$(cat utils/st2.version.txt) ./st2
pip install -r ./st2/requirements.txt
pip install -r ./st2/test-requirements.txt

