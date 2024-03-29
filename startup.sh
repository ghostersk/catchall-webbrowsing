#!/bin/bash
pip install -r requirements.txt
#python app.py
export FLASK_RUN_EXTRA_FILES="startup.sh"
export FLASK_DEBUG=True
export FLASK_RUN_HOST="0.0.0.0"
export FLASK_RUN_PORT=80

flask run & python app.py

#tail -f /dev/null
