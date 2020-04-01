# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<string:name>")
def hello(name):
    return f"Hello, {name}!"


@app.route("/hello", methods=["POST"])
def hello_form():
    name = request.form.get("name")
    return render_template("index_old.html", headline=name)


if __name__ == "__main__" or __name__ == "__builtin__":
    app.run()
