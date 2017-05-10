import os

from flask import json

with open('C:/Users/Izemir/Desktop/alquist-yaml-editor-master/bots/Cities/data/json_cities.txt') as json_file:
    data = json.load(json_file)
    for p in data['cities']:
        print('Name: ' + p['name'])
        print('Country: ' + p['country'])

        print('')