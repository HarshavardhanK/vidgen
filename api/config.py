#Configuration management

import os

DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
CUDA_VISIBLE_DEVICES = os.getenv('CUDA_VISIBLE_DEVICES', '0')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '1'))
TASK_TIME_LIMIT = int(os.getenv('TASK_TIME_LIMIT', '900'))
TASK_SOFT_TIME_LIMIT = int(os.getenv('TASK_SOFT_TIME_LIMIT', '840'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/output')
LOGS_DIR = os.getenv('LOGS_DIR', '/app/logs')

#env soecific overrides
if ENVIRONMENT == 'development':
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
elif ENVIRONMENT == 'production':
    DEBUG = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

#config object
class Config:
    def __init__(self):
        self.DATABASE_URL = DATABASE_URL
        self.REDIS_URL = REDIS_URL
        self.LOG_LEVEL = LOG_LEVEL
        self.ENVIRONMENT = ENVIRONMENT
        self.DEBUG = DEBUG
        self.CUDA_VISIBLE_DEVICES = CUDA_VISIBLE_DEVICES
        self.MAX_WORKERS = MAX_WORKERS
        self.TASK_TIME_LIMIT = TASK_TIME_LIMIT
        self.TASK_SOFT_TIME_LIMIT = TASK_SOFT_TIME_LIMIT
        self.OUTPUT_DIR = OUTPUT_DIR
        self.LOGS_DIR = LOGS_DIR

#Global config instance
config = Config()
