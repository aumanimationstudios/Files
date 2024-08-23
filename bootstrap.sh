#!/usr/bin/env bash
rm -rf files-env
python3 -m venv files-env
source files-env/bin/activate
unset PYTHONPATH
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
#echo "----- Created venv -------"
