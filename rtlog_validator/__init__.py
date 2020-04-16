# -*- coding: utf-8 -*-
"""Package to parse and validate RTLOGs"""

import logging

from .validator import Validator

VERSION = "0.0.1"
__AUTHOR__ = "Thiago Weidman (tw@weidman.com.br)"
__COPYRIGHT__ = "(C) 2014-2019 Thiago Weidman. GNU GPL 3 or later."

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
