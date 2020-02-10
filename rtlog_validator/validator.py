# -*- coding: utf-8 -*-
import json
import logging
from struct import Struct

from rtlog_validator.line_definitions import RTLOG

# Initial Program Setup
LOGGER = logging.getLogger(__name__)


class LineInfo(dict):
    """Class that holds line information"""

    def __init__(self, text, tag, line_format):
        logging.debug("Creating field")
        self["text"] = text
        self["tag"] = tag
        self["errors"] = []
        self.__rtlog_line_format = line_format

    def add_error(self, error):
        """Adds an error to the line error list"""
        self["errors"].append(error)

    def break_line(self):
        """Breaks the fields of the line and return them as a list"""
        bin_fields = Struct(self.__rtlog_line_format.struct_format).unpack_from(
            self["text"].encode()
        )
        return [field.decode("utf-8") for field in bin_fields]

    def validate_line_size(self):
        """Checks if the line has the correct size"""
        logging.debug(f"validate_line_size")
        # Removing 1 from text since the line break doesn't count
        if len(self["text"]) - 1 != self.__rtlog_line_format.tagSize():
            self.add_error("ERR_LINE_SIZE")
            return False
        return True

    def validate_line_terminator(self):
        """Checks if the line has the correct terminator (\\n)"""
        logging.debug(f"validate_line_terminator")
        if not self["text"][-1].__eq__("\n"):
            self.add_error("ERR_LINE_TERM")
            return False
        return True

    def validate_data_type(self):
        """Checks if the fields have the correct data type (string, number)"""
        logging.debug(f"validate_data_type")


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
                i
                + 1: LineInfo(
                    self.rtlog_dat[i],
                    self.rtlog_dat[i][0:5],
                    self.rtlog_format.get(self.rtlog_dat[i][0:5]),
                )
                for i in range(self.rtlog_dat.__len__())
            }
        )
        self.error_lines = []

    def __str__(self):
        return json.dumps(self)

    def __set_error(self, line_no):
        """Sets error_ind, if true there is errors on the RTLOG file"""
        self.error_ind = True
        if not line_no in self["error_lines"]:
            self.error_lines.append(line_no)

    def dump_separated(self, separator="|"):
        """Method to separate the RTLOG using a defined separator"""
        logging.debug(
            f"dumping rtlog_file ({self.__rtlog_file}) using separator = {separator}"
        )
        for line_no in self:
            print(separator.join(self[line_no].break_line()))

    def call_line_validators(self):
        """Call all methods from LineInfo class that contains validate_ in the name"""
        logging.debug(f"Calling all line validators")
        for line_no in self:
            for validator in [
                getattr(self[line_no], valmethod)
                for valmethod in dir(self[line_no])
                if "validate_" in valmethod
            ]:
                logging.debug(f"Method {validator} will be called for line {line_no}")
                if not validator():
                    logging.debug(f"Found error on line: {line_no}")
                    self.__set_error(line_no)


if __name__ == "__main__" or __name__ == "__builtin__":
    x = Validator()
    x.dump_separated()
