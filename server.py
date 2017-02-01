from flask import Flask, send_from_directory, send_file
from flask import request
from flask import redirect, url_for
from crossdomain import *
from werkzeug.utils import secure_filename
from shutil import copyfile
import json
import io
import main
import os
import zipfile
import urllib
import sys
import shutil

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = set(['yml', 'yaml', 'zip'])
ALLOWED_EXTENSIONS_TO_LOAD = set(['html'])

port = 5000
if len(sys.argv) > 1:
    port = sys.argv[1]

@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def getIndexPage():
    '''
    with io.open("index.html", "r", encoding="utf-8") as file:
        page = file.read()
        file.close()
        return page'''
    return send_file('index.html')

@app.route('/static/<path:path>')
def getStaticFiles(path):
    return send_from_directory('static', path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def getJsLibraries(path):
    for extension in ALLOWED_EXTENSIONS_TO_LOAD:
        if path.endswith(extension):
            with io.open(path, "r", encoding="utf-8") as file:
                page = file.read()
                file.close()
                return page
    print("Error: requested " + path)
    return "Error"


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
    return main.getYamlFile(str(d, 'utf-8'))


@app.route('/botnames', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def requestBotNames():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return main.getBotNames()


@app.route('/generate', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def generateNewGraph():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return main.createGraph(str(d, 'utf-8'))


def writeToFile(data):
    print("writing file")
    with io.open("bots/" + data["botname"].strip() + "/flows/" + data["filename"], "w", encoding="utf-8") as file:
        file.write(data["text"])
        file.close()


def recreateGraph(botName):
    print("recreating graph")
    main.createGraph(botName)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@crossdomain(origin='*')
def upload_file():
    if request.method == 'POST':
        botName = request.form['botname']
        print(request.data)
        print(request.form)
        print(request.files)
        # check if the post request has the file part
        if 'file' not in request.files:
            print("file not in request files")
            return "file not in request files"
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print("no selected file")
            return "no selected file"
        files = request.files.getlist("file")
        for file in files:
            print(file)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                checkUploadFolder()
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                print("saving file")
        createNewProject(botName)
    return "ok"


# creates a new folder for a bot and copies uploaded files there
def createNewProject(botName):

    path = "bots/" + botName + "/flows/"
    if not os.path.exists(path):
        os.makedirs(path)
    for file in os.listdir("temp"):
        copyfile("temp/" + file, path + file)
        os.remove("temp/" + file)

    '''
    path = "bots/" + botName + "/"
    if not os.path.exists(path):
        os.makedirs(path)


    for item in os.listdir("temp"):  # loop through items in dir
        print(item)
        if item.endswith(".zip"):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            print(file_name)
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall("temp")  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file

    copyFolder("", path, 0)

def copyFolder(pathFrom, pathTo, depth):
    if depth > 2:
        return
    for item in os.listdir("temp" + pathFrom):
        if item is "flows" or "states":
            try:
                shutil.copytree("temp/" + pathFrom + item, pathTo + item);
            except:
                print("error copying directory")
        elif os.path.isdir("temp/" + pathFrom + item):
            copyFolder(pathFrom + item + "/", pathTo, depth + 1)
            '''


# checks if upload folder exists, creates it not
def checkUploadFolder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)



app.run(
    debug=False,
    host="0.0.0.0",
    port=port
)
