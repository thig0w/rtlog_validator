# -*- coding: utf-8 -*-
import json
import logging
import re
from struct import Struct

from rtlog_validator.line_definitions import RTLOG

# Initial Program Setup
LOGGER = logging.getLogger(__name__)


class LineInfo(dict):
    """Class that holds line information"""

    def __init__(self, text, tag, line_format):
        super().__init__()
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

    def get_line_dict(self):
        """Breaks the filelds of the line and return them as a dict"""
        line_dict = {}
        bin_fields = Struct(self.__rtlog_line_format.struct_format).unpack_from(
            self["text"].encode()
        )
        line = [field.decode("utf-8") for field in bin_fields]
        for i in self.__rtlog_line_format:
            key = self.__rtlog_line_format[i]["name"].replace(" ", "_").lower()
            value = None if line[i - 1].strip().__eq__("") else line[i - 1].strip()
            if (
                self.__rtlog_line_format[i]["type"].__eq__("Number")
                and value is not None
            ):
                m = re.search(
                    "(\d) implied decimal", self.__rtlog_line_format[i]["desc"]
                )
                try:
                    power_factor = m.group(1)
                except AttributeError:
                    power_factor = 0
                finally:
                    value = float(value) / pow(10, int(power_factor))

            line_dict[key] = value
        return line_dict

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
        line = self.break_line()
        for i in range(len(line)):
            trimmed_field = line[i].strip()
            if self.__rtlog_line_format[i + 1]["type"].__eq__("Number") and (
                not trimmed_field.isdigit() and not trimmed_field.__eq__("")
            ):
                logging.debug(
                    f"Field {self.__rtlog_line_format[i + 1]['name']}, must be numeric, got {line[i]}"
                )
                self.add_error("ERR_FIELD_NUMBER")
                return False
        return True


class Validator(dict):
    """Loads a RTLOG.DAT file and validates it"""

    def __init__(
        self,
        format_file="RTLOG_format_14.1.3.csv",
        rtlog_file="C:\\Users\\LOGIC\\Desktop\\RTLOG_30010_20200125_20200128212026.DAT",
        rtlog_string=None,
    ):
        super().__init__()
        logging.debug(
            f"Initializing Validator: format_file = {format_file}, rtlog_file = {rtlog_file}"
        )
        self.__format_file = format_file
        self.__rtlog_file = rtlog_file
        self.error_ind = False
        self.rtlog_format = RTLOG(format_file)

        if rtlog_string is not None:
            self.rtlog_dat = rtlog_string.splitlines()
        else:
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
        if not line_no in self.error_lines:
            self.error_lines.append(line_no)

    def separate_file(self, separator="|"):
        logging.debug(
            f"separating rtlog_file ({self.__rtlog_file}) using separator = {separator}"
        )
        separated = []
        for line_no in self:
            separated.append(separator.join(self[line_no].break_line()))

        return "\n".join(separated)

    def dump_separated(self, separator="|"):
        """Method to separate the RTLOG using a defined separator"""
        logging.debug(
            f"dumping rtlog_file ({self.__rtlog_file}) using separator = {separator}"
        )
        print(self.separate_file(separator))

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

    def get_line_marks(self):
        """Get mark positions for the UI"""
        logging.debug(f"Dumping line position marks")
        marks = [
            {
                "line": line_no - 1,
                "start_pos": self.rtlog_format[self[line_no]["tag"]][field]["start"]
                + field
                - 1,
                "end_pos": self.rtlog_format[self[line_no]["tag"]][field]["end"]
                + field,
                "name": f"{self[line_no]['tag']}{field}",
            }
            for line_no in self
            for field in self.rtlog_format[self[line_no]["tag"]]
        ]
        logging.debug(f"Dumping tooltips")
        tooltips = [
            {
                "name": f"{tag}{field}",
                "infos": f"<b>{self.rtlog_format[tag][field]['name']}</b><br><u>Type:</u> {self.rtlog_format[tag][field]['type']}<br><u>Desc:</u> {self.rtlog_format[tag][field]['desc']}<br><u>Default:</u> {self.rtlog_format[tag][field]['default']}",
            }
            for tag in self.rtlog_format
            for field in self.rtlog_format[tag]
        ]
        return marks, tooltips


if __name__ == "__main__" or __name__ == "__builtin__":
    x = Validator()
    x.dump_separated()
    x.call_line_validators()
    x = Validator(
        rtlog_file="C:\\Users\\LOGIC\\Desktop\\RTLOG_30017_20200323_20200323143028.DAT"
    )
    # x2 = Validator(rtlog_file="C:\\Users\\LOGIC\\Desktop\\RTLOG_30000_20200320_20200320093012.DAT")
