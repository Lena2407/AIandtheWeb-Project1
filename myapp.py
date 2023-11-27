# myapp.py

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def start():
    return "<form action='reversed' method='get'><input name='rev'></input>< /form>" # remove space after < (Stud.IP display bug)

@app.route("/reversed")
def reversed():
    return "<h1>"+request.args.get('rev')[::-1]+"</h1>" # remove spaces after <, Stud.IP display bug

templates = {}
