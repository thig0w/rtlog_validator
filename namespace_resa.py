# -*- coding: utf-8 -*-

from flask_restplus import Namespace, Resource, fields

from rtlog_validator import Validator

namespace_resa = Namespace("api_resa", description="API operations")

model_line_mark = namespace_resa.model(
    "line_mark",
    {
        "line": fields.Integer(required=True, description="File line"),
        "start_pos": fields.Integer(required=True, description="Field start position"),
        "end_pos": fields.Integer(required=True, description="Field end position"),
        "name": fields.String(
            required=True, description="Name to be used as classname"
        ),
    },
)

model_tooltips = namespace_resa.model(
    "tooltips",
    {
        "name": fields.String(
            required=True, description="Name to be used as classname"
        ),
        "infos": fields.String(
            required=True, description="Information to be shown on the tooltip box"
        ),
    },
)

model_rtlog_field = namespace_resa.model(
    "rtlog_field",
    {
        "name": fields.String(required=True, description="Field Name"),
        "type": fields.String(required=True, description="Field type"),
        "size": fields.Integer(required=True, description="Field Size"),
        "start": fields.Integer(
            required=True, description="Field column start position"
        ),
        "end": fields.Integer(required=True, description="Field column end position"),
        "default": fields.String(required=True, description="Default Value"),
        "desc": fields.String(required=True, description="Field Description"),
    },
)

model_rtlog_line = namespace_resa.model(
    "rtlog_line",
    {
        "field_position": fields.Integer(
            required=True, description="field position in line", min=1
        ),
        "fields": namespace_resa.as_list(fields.Nested(model_rtlog_field)),
    },
)

model_rtlog_format = namespace_resa.model(
    "rtlog_format",
    {
        "tag": fields.String(required=True, description="Tag"),
        "line": namespace_resa.as_list(fields.List(fields.Nested(model_rtlog_line))),
    },
)

model_rtlog = namespace_resa.model(
    "rtlog",
    {
        "rtlog_string": fields.String(
            required=True, description="String with the RTLOG contents"
        ),
        "rtlog_format": namespace_resa.as_list(
            fields.List(fields.Nested(model_rtlog_format))
        ),
        "line_marks": namespace_resa.as_list(
            fields.List(fields.Nested(model_line_mark))
        ),
        "tooltips": namespace_resa.as_list(fields.List(fields.Nested(model_tooltips))),
    },
)

model_rtlog_string = namespace_resa.model(
    "rtlog_string",
    {
        "rtlog_string": fields.String(
            required=True, description="String with the RTLOG contents"
        )
    },
)


@namespace_resa.route("/validate/")
class ResaRTLOGValidate(Resource):
    @namespace_resa.marshal_list_with(model_rtlog)
    @namespace_resa.expect(model_rtlog_string)
    def post(self):
        """
        Run validation on the file sent
        """
        # args = validation_parser.parse_args()
        val = Validator(rtlog_string=namespace_resa.payload["rtlog_string"])

        rtlog_list = []
        for tag in val.rtlog_format:
            tag_list = {"tag": tag, "line": []}
            for field in val.rtlog_format[tag]:
                field_list = {
                    "field_position": field,
                    "fields": val.rtlog_format[tag][field],
                }
                tag_list["line"].append(field_list)
            rtlog_list.append(tag_list)

        marks, tooltips = val.get_line_marks()

        return {
            "rtlog_string": val.separate_file(),
            "rtlog_format": rtlog_list,
            "line_marks": marks,
            "tooltips": tooltips,
        }


@namespace_resa.route("/rtlog_format/")
class ResaRTLOGFormat(Resource):
    @namespace_resa.marshal_list_with(model_rtlog_format)
    @namespace_resa.expect(model_rtlog_string)
    def post(self):
        """
        Run validation on the file sent
        """
        # args = validation_parser.parse_args()
        val = Validator(rtlog_string=namespace_resa.payload["rtlog_string"])
        rtlog_list = []
        for tag in val.rtlog_format:
            tag_list = {"tag": tag, "line": []}
            for field in val.rtlog_format[tag]:
                field_list = {
                    "field_position": field,
                    "fields": val.rtlog_format[tag][field],
                }
                tag_list["line"].append(field_list)
            rtlog_list.append(tag_list)

        return rtlog_list
