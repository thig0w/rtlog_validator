# -*- coding: utf-8 -*-
import csv
import logging
import re

from rtlog_validator import get_data_path

# Initial Program Setup
LOGGER = logging.getLogger(__name__)

# Global Vars (This program may become a Class)
tagsDict = {}


class Field:
    """Common base class for all rtlog fields"""

    def __init__(self, name, type, size, default, desc):
        self.name = name
        self.type = type
        self.size = size
        self.default = default
        self.desc = desc


class Tag:
    """Common base class for all RTLOG tags"""

    def __init__(self, name):
        self.name = name
        self.fields = 0
        self.fieldsDict = {}

    def addField(self, fieldName, type, default, desc):
        logging.debug("Adding field <" + fieldName + "> to tag <" + self.name + ">")
        reType = re.match(r"(.*)\((.*)\)", type)
        self.fields += 1
        self.fieldsDict[self.fields] = Field(
            fieldName, reType.group(1), reType.group(2), default, desc
        )

    def tagSize(self):
        size = 0
        for i in self.fieldsDict:
            size += int(self.fieldsDict[i].size)
        return size


if __name__ == "__main__" or __name__ == "__builtin__":
    # Open csv file with rtlog configuration
    with open(get_data_path("RTLOG_format_14.1.3.csv"), "r") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=";")  # , quotechar='|')
        for row in spamreader:
            # Do nothing with the header
            if spamreader.line_num == 1:
                logging.debug("Reading RTLOG config header")
                continue
            # If column 1 has value start new tag definition
            if not (row[0].__eq__("")):
                logging.debug(
                    "Reading RTLOG new tag at file line #" + str(spamreader.line_num)
                )
                tag = Tag(row[0])
                tagsDict[tag.name] = tag
            # Add fields to tag
            tag.addField(row[1], row[2], row[3], row[4])
