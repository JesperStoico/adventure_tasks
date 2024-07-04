from flask import Flask, render_template, request, session
from flask_session import Session
import requests
import random
import pprint
import xml.etree.ElementTree as ET

from fetch_data import fetch_random_intro
import api_wowhead

app = Flask(__name__)


client_id = '97823a9d60c34c12ae4ba8d58889b1ca'
client_secret = 'L5tD2Cqs8RE2OWgXlIhsYtts12FMvj6o'
region = 'eu'
locale = 'en_GB'

missing_toys = []

def get_access_token():
    auth_response = requests.post(
        f'https://{region}.battle.net/oauth/token',
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'}
    )
    return auth_response.json()['access_token']

def get_all_toys(access_token):
    url = f'https://{region}.api.blizzard.com/data/wow/toy/index'
    params = {'namespace': 'static-eu', 'locale': locale}
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('toys', [])

def get_character_toys(realm_slug, character_name, access_token):
    url = f'https://{region}.api.blizzard.com/profile/wow/character/{realm_slug}/{character_name}/collections/toys'
    params = {'namespace': 'profile-eu', 'locale': locale}
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('toys', [])

def get_specific_toy(access_token, toy_id):
    url = f'https://{region}.api.blizzard.com/data/wow/toy/{toy_id}?namespace=static-10.2.7_54366-eu&locale=en_GB'
    
    params = {'namespace': 'profile-eu', 'locale': locale}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers, params=params)
    item_id = response.json()['item']['id']    

    url = f'https://{region}.api.blizzard.com/data/wow/item/{item_id}?namespace=static-10.2.7_54366-eu'
    response_item_data = requests.get(url, headers=headers, params=params)
    media_item_url = response_item_data.json()['preview_item']['media']['key']['href']

    url = media_item_url
    response_item_media = requests.get(url, headers=headers, params=params)

    return [response_item_data.json(), response_item_media.json()]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        character_name = request.form['character_name']
        realm_slug = request.form['realm_slug']
        
        access_token = get_access_token()
        session['access_token'] = access_token

        all_toys = get_all_toys(access_token)
        character_toys = get_character_toys(realm_slug, character_name, access_token)

        character_toy_ids = {toy['toy']['id'] for toy in character_toys}
        
        acquired_toys = [toy for toy in all_toys if toy['id'] in character_toy_ids]
        missing_toys = [toy for toy in all_toys if toy['id'] not in character_toy_ids]

        session['missing_toys'] = missing_toys
        
        return render_template('index.html', acquired_toys=acquired_toys, missing_toys=missing_toys, character_name=character_name, realm_slug=realm_slug)
    
    return render_template('index.html', acquired_toys=[], missing_toys=[], character_name='', realm_slug='')

@app.route('/give_task')
def give_task():
    access_token = session.get('access_token', [])
    # Retrieve missing_toys from session
    missing_toys = session.get('missing_toys', [])

    # Select a random toy from missing_toys list
    if missing_toys:
        random_toy = random.choice(missing_toys)
        random_toy_data = get_specific_toy(access_token, random_toy['id'])
        pprint.pprint(random_toy_data)
        
        wowhead_link = f"https://www.wowhead.com/item={random_toy_data[0]['id']}"
        
        return render_template(
            'give_task.html',
            data=random_toy_data[0],
            media=random_toy_data[1],
            greeting=fetch_random_intro(),
            wowhead_link=wowhead_link,
        )
    else:
        return "No missing toys available"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.run(debug=True)
