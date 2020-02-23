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

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None