import os
from os import getenv
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')