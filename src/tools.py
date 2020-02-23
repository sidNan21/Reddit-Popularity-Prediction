'''
tools.py
    simple script for useful functions
'''

import json

def save_json(data, filename=None):
    # provided no filename param, default to first post's id
    fn = filename if filename else data[0]['id']
    with open('./data/' + fn + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)