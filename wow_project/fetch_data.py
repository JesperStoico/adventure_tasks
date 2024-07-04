import os
import json
import random
from flask import jsonify

def fetch_random_intro():
    json_path = os.path.join(os.path.dirname(__file__), 'static\data', 'greetings.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        intro_texts = data['intro_texts']
        return random.choice(intro_texts)
