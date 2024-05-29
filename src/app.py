#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

from src import GetArgs, Promote, Update
import logging
import logging.handlers
from pathlib import Path

class App:
    """
        app provided by this script
    """

    def __init__(self):
        # create auxiliary variables
        logger_name = Path(__file__).stem

        # create logging formatter
        log_formatter = logging.Formatter(fmt=' %(name)s :: %(levelname)s :: %(message)s')

        # create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(log_formatter)

        # Add console handler to logger
        logger.addHandler(console_handler)

    def main(self):
        args = GetArgs()
        args.validate_options()
        if args.promote:
            promote = Promote()
            return promote.main(args)
        if args.update:
            update = Update()
            return update.main(args)

        return 0
