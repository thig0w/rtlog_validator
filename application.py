# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/<string:name>")
# def hello(name):
#     return f"Hello, {name}!"
#
#
# @app.route("/hello", methods=["POST"])
# def hello_form():
#     name = request.form.get("name")
#     return render_template("index_old.html", headline=name)


if __name__ == "__main__" or __name__ == "__builtin__":
    from namespace_resa import namespace_resa
    from flask_restplus import Api

    api = Api(
        app, version="0.1", title="RPK Api", description="Having fun", doc="/doc/"
    )
    api.add_namespace(namespace_resa)

    app.run()
