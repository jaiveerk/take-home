from flask import Flask
from flask_cors import CORS
import os
from unipath import Path

basedir = os.path.abspath(os.path.dirname(__file__))
BASEDIR = Path(__file__).parent
UPLOAD_FOLDER = '' # flask requires this var to be set to handle uploads (even though I never use it)
ALLOWED_EXTENTIONS = {'yml', 'yaml'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from app import routes