from dotenv import load_dotenv
from os import getenv
# from app import app

load_dotenv()
class Config():
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY = getenv('SECRET_KEY')
    DEBUG = getenv('DEBUG')