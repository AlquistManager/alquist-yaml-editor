from flask import Flask
from flask import request
from crossdomain import *
import json
import io
import main
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def update():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('UTF-8'))
        writeToFile(data)
        recreateGraph(data["botname"].strip())
    return "OK"


def writeToFile(data):
    print("writing file")
    with io.open("bots/" + data["botname"].strip() + "/flows/" + data["filename"], "w", encoding="utf-8") as file:
        file.write(data["text"])
        file.close()

def recreateGraph(botName):
    print("recreating graph")
    main.createGraph(botName)