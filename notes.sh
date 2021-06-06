# commands and notes to setup and use 
# Flask Virtual Environemnts for Development

# pyenv exec python3 -m venv .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# pip install Flask 

export FLASK_APP=app.py
export FLASK_ENV=development

flask run
