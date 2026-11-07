#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template

DEVELOPMENT_ENV = True

app = Flask(__name__)

app_data = {
    "name": "Drukāšanas plāna optimizācija",
    "description": "Grāmatu drukāšanas pasūtījumu plānošanas sistēma",
    "author": "ProjLab6k",
    "html_title": "Drukāšanas plāna optimizācija",
    "project_name": "TBDPRINTSOS",
    "keywords": "drukāšana, optimizācija, grāmatas, plānošana",
}

@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


@app.route("/service")
def service():
    return render_template("service.html", app_data=app_data)


@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
