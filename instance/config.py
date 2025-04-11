import os

SECRET_KEY = os.urandom(24)
STRIPE_API_KEY = 'gen_apikey_her'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin_db:admin_password_her@localhost:3306/infralinker_db'
SQLALCHEMY_POOL_RECYCLE = 60
