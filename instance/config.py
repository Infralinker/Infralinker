import os

SECRET_KEY = os.urandom(24)
STRIPE_API_KEY = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin_db:9UcZJxdB440TqguLfUYTQgh3I@localhost:3306/infralinker_db'
SQLALCHEMY_POOL_RECYCLE = 60
