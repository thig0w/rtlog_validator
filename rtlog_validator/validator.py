# -*- coding: utf-8 -*-
import json
import logging
from struct import Struct

from rtlog_validator.line_definitions import RTLOG

# Initial Program Setup
LOGGER = logging.getLogger(__name__)


class Validator(dict):
    """Loads a RTLOG.DAT file and validates it"""

    def __init__(
        self,
        format_file="RTLOG_format_14.1.3.csv",
        rtlog_file="C:\\Users\\LOGIC\\Desktop\\RTLOG_30010_20200125_20200128212026.DAT",
    ):
        logging.debug(
            f"Initializing Validator: format_file = {format_file}, rtlog_file = {rtlog_file}"
        )
        self.__format_file = format_file
        self.__rtlog_file = rtlog_file
        self.error_ind = False
        self.rtlog_format = RTLOG(format_file)
        logging.debug(f"Open File")
        with open(rtlog_file, "r") as f:
            self.rtlog_dat = f.readlines()
        logging.debug(f"Building dictionary")
        self.update(
            {
                i + 1: {"text": self.rtlog_dat[i], "tag": self.rtlog_dat[i][0:5]}
                for i in range(self.rtlog_dat.__len__())
            }
        )

    def __str__(self):
        return json.dumps(self)

    def dump_separated(self, separator=b"|"):
        logging.debug(
            f"dumping rtlog_file ({self.__rtlog_file}) using separator = {separator}"
        )
        for line_no in self:
            format = self.rtlog_format[self[line_no]["tag"]].struct_format
            print(separator.join(Struct(format).unpack_from(self[line_no])))

    def validate_size(self):
        logging.debug(f"Validating size of rtlog_file = {self.__rtlog_file}")
        for line_no in self:
            if (
                self.rtlog_format[self[line_no]["tag"]].tagSize()
                != len(self[line_no]["text"]) - 1
            ):
                logging.debug(f"Found line size error")
                self[line_no]["errors"] = "ERR_LINE_SIZE"
                self.error_ind = True


if __name__ == "__main__" or __name__ == "__builtin__":
    x = Validator()
