import os

SECRET_KEY = os.urandom(24)
STRIPE_API_KEY = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin_db:admin_passwd_to_change@localhost:3306/infralinker_db'
SQLALCHEMY_POOL_RECYCLE = 60
