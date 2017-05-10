
import os

from flask import json

data = {}
data['cities'] = []
data['cities'].append({
    'name': 'Prague',
    'country': 'Czech Republic',
    'synonyms': 'Praha, Praag',
})
data['cities'].append({
    'name': 'Antananarivo',
    'country': 'Madagascar',
})
data['cities'].append({
    'name': 'Moscow',
    'country': 'Russian Federation',
})



with open('C:/Users/Izemir/Desktop/alquist-yaml-editor-master/bots/Cities/data/json_cities.txt', 'w') as f:
    json.dump(data, f)