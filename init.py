#!/usr/bin/env python

import argparse
import logging.config
import sys
import src.main

if __name__ == '__main__':

    DEFAULT_LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            '': {
                'level': 'INFO',
            },
            'another.module': {
                'level': 'DEBUG',
            },
        }
    }

    logging.config.dictConfig(DEFAULT_LOGGING)

    parser = argparse.ArgumentParser()
    parser.add_argument('-cloud', dest='cloud', help='Select [azure], [aws] or [gcp] Sample. e.g. -cloud aws')
    args = parser.parse_args()
    sys.exit(src.main.main(args))
