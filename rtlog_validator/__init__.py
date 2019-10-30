# -*- coding: utf-8 -*-
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    return os.path.join(_ROOT, "data", path)


print(get_data("resource1/foo.txt"))
