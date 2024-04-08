import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY =  os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS =  os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    UPLOAD_FOLDER =  os.getenv('UPLOAD_FOLDER')
    ALLOWED_EXTENSIONS =  os.getenv('ALLOWED_EXTENSIONS')
    JWT_SECRET_KEY =  os.getenv('JWT_SECRET_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT =  os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME =  os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD =  os.getenv('MAIL_PASSWORD')
