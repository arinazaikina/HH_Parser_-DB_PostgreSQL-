import logging.config

dict_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'base': {
            'format': '%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s'
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'DEBUG',
            'formatter': 'base',
        },

        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'base',
            'filename': 'logfile.log',
            'mode': 'a',
        }
    },

    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['file']
        },

        'db_logger': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False
        },

        'hh_logger': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False
        }
    }
}

logging.config.dictConfig(config=dict_config)
db_logger = logging.getLogger('db_logger')
hh_logger = logging.getLogger('hh_logger')
