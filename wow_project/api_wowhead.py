import requests

def get_item_data(item_id):
    url = f"https://www.wowhead.com/item={item_id}&xml"
    response = requests.get(url)

    if response.status_code == 200:
        print(item_id, response.text, response.status_code)
        return response.text
    else:
        return None
