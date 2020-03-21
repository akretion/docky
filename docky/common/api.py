# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
import sys
# Optionnal code for colorized log
from rainbow_logging_handler import RainbowLoggingHandler

logger = logging.getLogger('docky')
formatter = logging.Formatter("%(message)s")
logger.setLevel(logging.INFO)

handler = RainbowLoggingHandler(
    sys.stderr,
    color_message_info=('green', None, True),
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def raise_error(message):
    logger.error(message)
    sys.exit(0)
