# -*- coding: utf-8 -*-
"""Package to parse and validate RTLOGs"""

import logging
import os
import re

from .validator import Validator

VERSION = "0.0.1"
__AUTHOR__ = "Thiago Weidman (tw@weidman.com.br)"
__COPYRIGHT__ = "(C) 2014-2019 Thiago Weidman. GNU GPL 3 or later."

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_rtlog_format_versions():
    data_path = os.path.join(_ROOT, "data")
    file_list = os.listdir(data_path)
    regex = re.compile("(\d{2}\.\d+\.\d+)")
    return {
        regex.search(file).group(): file for file in file_list if regex.search(file)
    }
