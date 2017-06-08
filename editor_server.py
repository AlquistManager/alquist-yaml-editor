import json
import os
import shutil
import zipfile

from flask import Flask, send_from_directory, send_file, Blueprint
from werkzeug.utils import secure_filename

import graph_generator
import io
import loggers
from crossdomain import *

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = set(['zip', 'py', 'yml', 'txt', 'json'])
ALLOWED_EXTENSIONS_TO_LOAD = set(['html'])

editor = Blueprint('editor', __name__, static_url_path='/static')


# index page with project selection
@editor.route('/editor/')
def getIndexPage():
    return send_file('index.html')


# static files (javascript libraries, stylesheets, themes)
@editor.route('/static-files/<path:path>')
def getStaticFiles(path):
    print("path: " + path)
    return send_file(os.path.join('static-files', path))


@editor.route('/static-files/themes/<path:path>')
def getTheme(path):
    return send_file(os.path.join('static-files', 'themes', path))


@editor.route('/static-files/bootstrap/js/<path:path>')
def get_js(path):
    return send_file(os.path.join('static-files', 'bootstrap', 'js', path))


@editor.route('/static-files/bootstrap/fonts/<path:path>')
def get_font(path):
    return send_file(os.path.join('static-files', 'bootstrap', 'fonts', path))


@editor.route('/static-files/bootstrap/css/<path:path>')
def get_css(path):
    return send_file(os.path.join('static-files', 'bootstrap', 'css', path))


# returns all static files from root folder with allowed extensions (html)
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


# receives updated yaml code in POST request, generates new graph
@editor.route('/editor/update', methods=['POST'])
def update():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('UTF-8'))
        writeToFile(data)
        response = recreateGraph(data["botname"].strip())
    return response;


# returns graph file to display
@editor.route('/editor/graph', methods=['POST'])
def requestGraphFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getGraphFile()


# returns file with positions of states in yaml files
@editor.route('/editor/statepos', methods=['POST'])
def requestStatePosFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getStatePositionsFile()


# returns requested yaml file
@editor.route('/editor/getfile', methods=['POST'])
def requestYamlFile():
    if request.method == 'POST':
        d = request.get_data()
        print(d)
    return graph_generator.getYamlFile(str(d, 'utf-8'))


# returns names of available bot projects
@editor.route('/editor/botnames', methods=['POST'])
def requestBotNames():
    return graph_generator.getBotNames()


# creates a new graph for bot specified in POST request data
@editor.route('/editor/generate', methods=['POST'])
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
    print(data)
    file_path = os.path.join("bots", data["botname"].strip(), data["folder"], data["filename"])
    with io.open(file_path, "w", encoding="utf-8") as file:
        file.write(data["text"])
        file.close()


# recreate graph of given bot
def recreateGraph(botName):
    print("recreating graph")
    return graph_generator.createGraph(botName)


# checks whether given file has allowed extension
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
        if 'botname' not in request.form:
            return "request missing attributes"
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
            if 'files[]' not in request.files:
                print("file not in request files")
                return "file not in request files"
            files = request.files.getlist("files[]")
            for file in files:
                print(file)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    checkUploadFolder(UPLOAD_FOLDER)
                    checkUploadFolder(os.path.join("bots", botName, "states"))
                    file.save(os.path.join(UPLOAD_FOLDER, filename))

                    if os.path.splitext(filename)[1] == ".py":
                        save_path = os.path.join("bots", botName, "states")
                    elif os.path.splitext(filename)[1] == ".yml":
                        save_path = os.path.join("bots", botName, "flows")
                    else:
                        save_path = os.path.join("bots", botName, "other")

                    if not os.path.exists(save_path):
                        os.mkdir(save_path)

                    if os.path.exists(os.path.join(save_path, filename)):
                        os.remove(os.path.join(save_path, filename))
                    shutil.move(os.path.join(UPLOAD_FOLDER, filename), save_path)
                    print("saving file")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


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
            zipf.write(os.path.abspath(os.path.join(root, filename)), arcname=relpath)
    zipf.close()
    print("directory: " + os.path.abspath(directory) + " path: " + path + ".zip")
    return send_from_directory(os.path.abspath(directory), path + ".zip")


# creates a new file or folder
@editor.route('/editor/newfile', methods=['POST'])
def createNewFile():
    if request.method == 'POST':
        print(request.get_data())
        data = json.loads(request.get_data().decode('UTF-8'))
        print(data)
        if data['type'] == "folder":
            os.mkdir(os.path.join("bots", data['botname'], data['name']))
            return "ok"
        else:
            save_dir = save_path = os.path.join("bots", data['botname'], data['folder'])
            save_path = os.path.join("bots", data['botname'], data['folder'], data['name'])
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
        with io.open(save_path, 'a', encoding="utf-8") as file:
            file.close()
        return "ok"


# deletes selected file or folder
@editor.route('/editor/deletefile', methods=['POST'])
def deleteFile():
    if request.method == 'POST':
        print(request.get_data())
        data = json.loads(request.get_data().decode('UTF-8'))
        if data["botname"] == data["folder"]:
            path = os.path.join("bots", data["folder"], data["filename"])
            shutil.rmtree(path)
        else:
            path = os.path.join("bots", data["botname"], data["folder"], data["filename"])
            os.remove(path)
        return "ok"


# returns html page with graph and code editor
@editor.route('/editor/graphpage', methods=['GET'])
def openGraph():
    botname = request.args.get('bot')
    return send_file('editor.html')


# deletes specified bot project
@editor.route('/editor/delete-project', methods=['POST'])
def deleteProject():
    botname = str(request.get_data(), 'utf-8')
    try:
        loggers.handlers.get(botname.lower()).get("db_handler").close()
        loggers.handlers.get(botname.lower()).get("nfo_handler").close()
    except:
        print("no handlers")
    shutil.rmtree(os.path.join("bots", botname))
    return graph_generator.getBotNames()


# creates a new folder for a bot and copies uploaded files in there
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


# checks if upload folder exists, creates it if doesn't
def checkUploadFolder(upload_fold):
    if not os.path.exists(upload_fold):
        os.makedirs(upload_fold)


# creates empty folder structure for a new bot project (flows and states folders)
def createEmptyFolderStructure(botname):
    flowsPath = "bots/" + botname + "/flows"
    statesPath = "bots/" + botname + "/states"
    if not os.path.exists(flowsPath):
        os.makedirs(flowsPath)
    if not os.path.exists(statesPath):
        os.makedirs(statesPath)
