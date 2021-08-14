#!/bin/bash
# The runner to serve our flask app.

if [[ ! -f vaccines.py ]]; then
    echo "Run me from project root: cd <project_root> && ./runner.sh"
    exit 1
fi

if ! command -v python >/dev/null; then
    echo 'You must have python installed and in $PATH to run this.'
    exit 1
fi

version="$(python --version)"
if [[ ${version} != 'Python 3.9.6' ]]; then
    echo "This app has been tested on Python 3.9.6, but you are running ${version}."
    echo "Your mileage may or may not vary."
fi

if [[ ! -d env ]]; then
    python -m venv env
fi
source env/bin/activate
pip install -r requirements.txt

export FLASK_ENV=development
export FLASK_APP=vaccines
flask run --host=0.0.0.0
