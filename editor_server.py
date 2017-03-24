import io
import json
import os
import shutil
import sys
import zipfile

from flask import Flask, send_from_directory, send_file, Blueprint, render_template
from werkzeug.utils import secure_filename

import graph_generator
from crossdomain import *

app = Flask(__name__, static_url_path='/static') #, static_url_path='/static'
UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = set(['zip','py','yml'])
ALLOWED_EXTENSIONS_TO_LOAD = set(['html'])

'''
port = 3000
if len(sys.argv) > 1:
    port = sys.argv[1]
'''

editor = Blueprint('editor', __name__, static_url_path='/static') #, static_url_path='/static'

# index page with project selection
@editor.route('/editor/', methods=['POST', 'GET', 'OPTIONS'])
def getIndexPage():
    return send_file('index.html')

# static files (javascript libraries, stylesheets, themes)
@editor.route('/static-files/<path:path>')
def getStaticFiles(path):
    print("path: " + path)
    #return "nothing here"
    #return send_file(os.path.join(os.getcwd, 'static', path))
    return send_file(os.path.join('static-files', path))
    #return send_from_directory('static-files', path)

@editor.route('/static-files/themes/<path:path>')
def getTheme(path):
    return send_file(os.path.join('static-files', 'themes', path))


# returns all static files with allowed extensions (html)
@editor.route('/', defaults={'path': ''})
@editor.route('/<path:path>')
def getJsLibraries(path):
    for extension in ALLOWED_EXTENSIONS_TO_LOAD:
        if path.endswith(extension):
            with io.open(path, "r", encoding="utf-8") as file:
                page = file.read()
                file.close()
                return page
    print("Error: requested " + path)
    return "Error"

# update graph with new yaml code
@editor.route('/editor/update', methods=['POST', 'GET', 'OPTIONS'])
def update():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('UTF-8'))
        writeToFile(data)
        response = recreateGraph(data["botname"].strip())
    return response;

# returns graph file for display
@editor.route('/editor/graph', methods=['POST', 'GET', 'OPTIONS'])
def requestGraphFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getGraphFile()

# returns file with positions of states in yaml files
@editor.route('/editor/statepos', methods=['POST', 'GET', 'OPTIONS'])
def requestStatePosFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getStatePositionsFile()

# returns requested yaml file
@editor.route('/editor/getfile', methods=['POST', 'GET', 'OPTIONS'])
def requestYamlFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getYamlFile(str(d, 'utf-8'))

# returns names of available bot projects
@editor.route('/editor/botnames', methods=['POST', 'GET', 'OPTIONS'])
def requestBotNames():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getBotNames()

# creates a new graph
@editor.route('/editor/generate', methods=['POST', 'GET', 'OPTIONS'])
def generateNewGraph():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.createGraph(str(d, 'utf-8'))

# returns yaml filenames in a html list to be displayed by jstree
@editor.route('/editor/filenamesHtml', methods=['POST'])
def getYamlFileNamesHtml():
    if request.method == 'POST':
        projectName = str(request.get_data(), 'utf-8')
        return graph_generator.getYamlNamesHtml(projectName)

# returns yaml filenames
@editor.route('/editor/filenames', methods=['POST'])
def getYamlFileNames():
    if request.method == 'POST':
        projectName = str(request.get_data(), 'utf-8')
        return graph_generator.getYamlNames(projectName)

# write yaml code to file
def writeToFile(data):
    print("writing file")
    with io.open("bots/" + data["botname"].strip() + "/flows/" + data["filename"], "w", encoding="utf-8") as file:
        file.write(data["text"])
        file.close()

# recreate graph of given bot
def recreateGraph(botName):
    print("recreating graph")
    return graph_generator.createGraph(botName)

# checks given file has allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# upload files
@editor.route('/editor/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.data)
        print(request.form)
        print(request.files)
        botName = request.form['botname']
        if request.form['form'] == 'create_project':
            # check if the post request has the file part
            if 'file' not in request.files:
                print("file not in request files")
                createEmptyFolderStructure(botName)
                return "file not in request files"
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                print("no selected file")
                createEmptyFolderStructure(botName)
                return "no selected file"
            files = request.files.getlist("file")
            for file in files:
                print(file)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    checkUploadFolder(UPLOAD_FOLDER)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    print("saving file")
            createNewProject(botName)
        elif request.form['form'] == 'python':
            # check if the post request has the file part
            if 'file' not in request.files:
                print("file not in request files")
                return "file not in request files"
            #file = request.files['file']
            files = request.files.getlist("file")
            for file in files:
                print(file)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    checkUploadFolder(UPLOAD_FOLDER)
                    checkUploadFolder(os.path.join("bots", botName, "states"))
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    shutil.move(os.path.join(UPLOAD_FOLDER, filename), os.path.join("bots", botName, "states"))
                    print("saving file")
    return "ok"

# download bot project in a zip file
@editor.route('/editor/download/<path:path>', methods=['GET', 'POST'])
def download_file(path):
    print("download file")
    directory = os.getcwd() + "/bots"
    zipf = zipfile.ZipFile('{0}.zip'.format(os.path.join(os.getcwd(), "bots/" + path)), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "bots/" + path)):
        for filename in files:
            relpath = os.path.relpath(os.path.join(root, filename), directory + "/path")
            relpath = relpath[2:]
            print(relpath)
            zipf.write(os.path.abspath(os.path.join(root, filename)),
                       arcname=relpath)  # os.path.abspath(os.path.join(root, filename)), arcname=filename
    zipf.close()
    print("directory: " + os.path.abspath(directory) + " path: " + path + ".zip")
    return send_from_directory(os.path.abspath(directory), path + ".zip")

# creates a new yaml file
@editor.route('/editor/newfile', methods=['POST'])
def createNewFile():
    if request.method == 'POST':
        print(request.get_data())
        data = str(request.get_data((), 'utf-8')).split(";")
        new_file_name = data[0] + ".yml"
        bot_name = data[1]
        with io.open("bots/" + bot_name + "/flows/" + new_file_name, 'a', encoding="utf-8") as file:
            file.close()
        return "ok"

# deletes selected yaml file
@editor.route('/editor/deletefile', methods=['POST'])
def deleteFile():
    if request.method == 'POST':
        print(request.get_data())
        data = str(request.get_data((), 'utf-8')).split(";")
        os.remove("bots/" + data[1] + "/flows/" + data[0])
        return "ok"

@editor.route('/editor/graphpage', methods=['GET'])
def openGraph():
    botname = request.args.get('bot')
    return send_file('test_viz_js2.html')


# creates a new folder for a bot and copies uploaded files there
def createNewProject(botName):
    path = "bots/" + botName + "/"
    if not os.path.exists(path):
        os.makedirs(path)
    for item in os.listdir("temp"):  # loop through items in dir
        if item.endswith(".zip"):  # check for ".zip" extension
            os.chdir("temp")
            file_name = os.path.abspath(item)  # get full path of files
            os.chdir("..")
            print(file_name)
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall("temp")  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file
            tmp_path = "temp/" + item[:-4]
            break
    copyFolder("", path, 0)
    shutil.rmtree(tmp_path)

# copy files from temp to bots folder
def copyFolder(pathFrom, pathTo, depth):
    if depth > 2:
        return
    for item in os.listdir("temp/" + pathFrom):
        if (item == "flows") or (item == "states"):
            try:
                shutil.copytree("temp/" + pathFrom + item, pathTo + item);
            except:
                print("error copying directory")
        elif os.path.isdir("temp/" + pathFrom + item):
            copyFolder(pathFrom + item + "/", pathTo, depth + 1)


# checks if upload folder exists, creates it if not
def checkUploadFolder(upload_fold):
    if not os.path.exists(upload_fold):
        os.makedirs(upload_fold)

#creates empty folder structer for a new bot project
def createEmptyFolderStructure(botname):
    flowsPath = "bots/" + botname + "/flows"
    statesPath = "bots/" + botname + "/states"
    if not os.path.exists(flowsPath):
        os.makedirs(flowsPath)
    if not os.path.exists(statesPath):
        os.makedirs(statesPath)

'''
# runs flask application
app.run(
    debug=False,
    host="0.0.0.0",
    port=port
)
'''