import os

user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]

SECRET_KEY = os.urandom(24)
STRIPE_API_KEY = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@localhost:3306/infralinker_db"
SQLALCHEMY_POOL_RECYCLE = 60
