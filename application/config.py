from dotenv import load_dotenv
from os import getenv
# from app import app

load_dotenv()
class Config():
    # SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'postgres://postgres.ujuwconmtcvdgikxvqcr:Zr1RhFgbTywGFOg8@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x')
    SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY = getenv('SECRET_KEY')
    DEBUG = getenv('DEBUG')