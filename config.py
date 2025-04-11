class Config(object):
    """
    Common configurations
    """
    ### SMTP CONFIG FOR INTERNAL SERVER AS RELAY SERVER (USER MUST CONFIG SENDMAIL)

    APP_NAME = 'INFRALINKER PROJECT'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25

    WTF_CSRF_TIME_LIMIT = None
    BOOTSTRAP_SERVE_LOCAL = False


    BOOTSTRAP_MSG_CATEGORY = 'danger'
    BOOTSTRAP_ICON_SIZE = '23px'
    BOOTSTRAP_ICON_COLOR = 'light'

    #You can change the theme by changing the value of BOOTSTRAP_BOOTSWATCH_THEME
    BOOTSTRAP_BOOTSWATCH_THEME = 'lumen' #flatly #cosmo #Yeti #lumen
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_CDN_FORCE_SSL = True

       
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx', 'xls', 'xlsx'])
    
    #GZip Compression 
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'application/json',
        'application/javascript'
        ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    COMPRESS_CACHE_KEY = None
    COMPRESS_CACHE_BACKEND = None
    COMPRESS_REGISTER = True

class DevelopmentConfig(Config):
    """
    Development configurations
    """
    SQLALCHEMY_ECHO = True
    DEBUG = True

class ProductionConfig(Config):
    """
    Production configurations
    """
    SQLALCHEMY_ECHO = False
    DEBUG = False
    
class TestingConfig(Config):
    """
    Testing configurations
    """
    TESTING = True
    
app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
