#!/usr/bin/env python

import os.path
import sys

from logging import getLogger
import logbook
from logbook import NestedSetup, NullHandler, FileHandler, MailHandler, \
        StreamHandler, TimedRotatingFileHandler
from logbook.compat import RedirectLoggingHandler, redirect_logging

from apps import generate_app


def main(argv=None):

    if not argv:
        argv = 'settings.py'
    config_location = os.path.abspath(argv)

    logger = NestedSetup([
        NullHandler(),
        StreamHandler(sys.stdout, level='DEBUG', bubble=True),
        #TimedRotatingFileHandler('log/webpi.log',
        #    level='DEBUG',
        #    bubble=True),
        ])

    app = generate_app(config_location)
    log = getLogger(app.config['LOGGER_NAME'])
    redirect_logging()
    with logger.applicationbound():
        if app.debug:
            app.run('0.0.0.0')
        else:
            app.run()
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
