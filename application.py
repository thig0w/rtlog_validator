# -*- coding: utf-8 -*-

from flask import Flask, render_template
from namespace_resa import namespace_resa
from flask_restplus import Api

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


api = Api(
    app,
    version="0.1",
    title="RPK Api",
    description="RPK apis used on the web application",
    doc="/doc/",
)
api.add_namespace(namespace_resa)

if __name__ == "__main__" or __name__ == "__builtin__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port)
