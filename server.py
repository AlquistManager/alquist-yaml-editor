from flask import Flask
from flask import request
from crossdomain import *
import json
import io
import main
import os
import urllib
import sys

app = Flask(__name__)

port = 5000
if len(sys.argv) > 1:
    port = sys.argv[1]

@app.route('/update', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def update():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('UTF-8'))
        writeToFile(data)
        recreateGraph(data["botname"].strip())
    return "OK"


@app.route('/graph', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def requestGraphFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return main.getGraphFile()

@app.route('/statepos', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def requestStatePosFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return main.getStatePositionsFile()

@app.route('/getfile', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def requestYamlFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return main.getYamlFile(str(d,'utf-8'))


def writeToFile(data):
    print("writing file")
    with io.open("bots/" + data["botname"].strip() + "/flows/" + data["filename"], "w", encoding="utf-8") as file:
        file.write(data["text"])
        file.close()


def recreateGraph(botName):
    print("recreating graph")
    main.createGraph(botName)


app.run(
        debug=False,
        host="0.0.0.0",
        port=port
    )
