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


@app.route('/', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def requestFiles():
    if request.method == 'POST':
        r = ['<ul class="jqueryFileTree" style="display: none;">']
        d = request.get_data()
        print(d)

        r = "<ul>"
        for f in os.listdir('.'):
            r += "<il>" + f + "</li>"

        r += "</ul>"


        '''
        try:
            r = ['<ul class="jqueryFileTree" style="display: none;">']
            d = request.get_data()

            d = urllib.unquote(request.POST.get('dir', 'c:\\temp'))
            for f in os.listdir(d):
                ff = os.path.join(d, f)
                if os.path.isdir(ff):
                    r.append('<li class="directory collapsed"><a rel="%s/">%s</a></li>' % (ff, f))
                else:
                    e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                    r.append('<li class="file ext_%s"><a rel="%s">%s</a></li>' % (e, ff, f))
            r.append('</ul>')
        except Exception, e:
            r.append('Could not load directory: %s' % str(e))
        r.append('</ul>')
        return HttpResponse(''.join(r))'''
    return r


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
