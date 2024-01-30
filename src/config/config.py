RUNTIME_HOST = "0.0.0.0"      # 监听地址
RUNTIME_PORT = 23333        # 监听端口
RUNTIME_DEBUG = True        # 调试信息

class AppConfig(object):
    SQLALCHEMY_DATABASE_URI = '' # URL connecting to your database 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True