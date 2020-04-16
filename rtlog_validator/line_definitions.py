# -*- coding: utf-8 -*-
import csv
import json
import logging
import os
import re

# from rtlog_validator import get_data_path

# Initial Program Setup
LOGGER = logging.getLogger(__name__)
_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data_path(path):
    return os.path.join(_ROOT, "data", path)


class Field(dict):
    """Common base class for all rtlog fields"""

    def __init__(self, name, type, size, default, desc, start_pos):
        logging.debug("Creating field")
        self["name"] = name
        self["type"] = type
        self["size"] = size
        self["start"] = start_pos
        self["end"] = start_pos + size - 1
        self["default"] = default
        self["desc"] = desc


class Tag(dict):
    """Common base class for all RTLOG tags"""

    def __init__(self, name):
        self.name = name
        self.__start_pos = 0
        self.struct_format = ""

    def addField(self, fieldName, type, default, desc):
        logging.debug("Adding field <" + fieldName + "> to tag <" + self.name + ">")
        reType = re.match(r"(.*)\((.*)\)", type)
        self[self.__len__() + 1] = Field(
            fieldName,
            reType.group(1),
            int(reType.group(2)),
            default,
            desc,
            self.__start_pos,
        )
        self.__start_pos += int(reType.group(2))
        self.struct_format += f"{reType.group(2)}s"

    def tagSize(self):
        size = 0
        for i in self:
            size += int(self[i]["size"])
        return size


class RTLOG(dict):
    """RTLOG file definition"""

    def __init__(self, format_file="RTLOG_format_14.1.3.csv"):
        # Open csv file with rtlog configuration
        with open(get_data_path(format_file), "r") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=";")  # , quotechar='|')
            for row in spamreader:
                # Do nothing with the header
                if spamreader.line_num == 1:
                    logging.debug("Reading RTLOG config header")
                    continue
                # If column 1 has value start new tag definition
                if not (row[0].__eq__("")):
                    logging.debug(
                        "Reading RTLOG new tag at file line #"
                        + str(spamreader.line_num)
                    )
                    tag = Tag(row[0])
                    self[tag.name] = tag
                # Add fields to tag
                tag.addField(row[1], row[2], row[3], row[4])

    def __str__(self):
        return json.dumps(self)


if __name__ == "__main__" or __name__ == "__builtin__":
    rtlog = RTLOG("RTLOG_format_14.1.3.csv")
    fh = b"FHEAD0000000001RTLG202002041735292020020430017                                   POS"
    from struct import Struct

    print(b"|".join(Struct(rtlog["FHEAD"].struct_format).unpack_from(fh)))
