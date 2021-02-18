from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, world!"

@app.route("/login")
def vdo_test():
    return render_template("login.html")