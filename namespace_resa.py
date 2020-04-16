# -*- coding: utf-8 -*-
from flask_restplus import Namespace, Resource, fields

from rtlog_validator import Validator

namespace_resa = Namespace("api_resa", description="API operations")

model_rtlog = namespace_resa.model(
    "rtlog",
    {
        "rtlog_string": fields.String(
            required=True, description="String with the RTLOG contents"
        )
    },
)


class ResaString(fields.Raw):
    def format(self, value):
        return value.rtlog_string


@namespace_resa.route("/validate/")
class ResaRTLOGValidate(Resource):
    # @namespace_resa.doc(model='ValidatorModel', body=ResaString)
    @namespace_resa.marshal_list_with(model_rtlog)
    @namespace_resa.expect(model_rtlog)
    def post(self):
        """
        Run validation on the file sent
        """
        # args = validation_parser.parse_args()
        val = Validator(rtlog_string=namespace_resa.payload["rtlog_string"])
        return {"rtlog_string": val.separate_file()}
