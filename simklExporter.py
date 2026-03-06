import requests
import csv
import configparser

def make_request(url, headers=None):
    response = requests.get(url, headers=headers)
    return response.json()

def make_csv(data):
    with open('./simkl_letterboxd_export.csv', 'w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Title",
            "Year",
            "IMDb ID",
            "TMDb ID",
            "Type",
            "Status"
        ])

        for item in data:
            writer.writerow([
                item.get("title"),
                item.get("year"),
                item.get("imdb"),
                item.get("tmdb"),
                item.get("type"),
                item.get("status")
            ])

config = configparser.ConfigParser()
config.read('conf.ini')

client_id = config["CONFIGS"]["client_id"]

get_pin_url = "https://api.simkl.com/oauth/pin?client_id=" + client_id
pin_request = make_request(get_pin_url)

user_code = pin_request['user_code']
verification_url = pin_request['verification_url']

is_user_authenticated = False
code_verification_url = "https://api.simkl.com/oauth/pin/" + user_code + "?client_id=" + client_id

while not is_user_authenticated:
    print("go to", verification_url)
    print("enter code:", user_code)
    input("press enter after confirming...")

    code_verification_request = make_request(code_verification_url)

    if 'access_token' in code_verification_request:
        access_token = code_verification_request['access_token']
        is_user_authenticated = True

endpoints = [
    ("movies","completed"),
    ("movies","plantowatch"),
    ("tv","plantowatch"),
    ("tv","completed"),
    ("anime","plantowatch"),
    ("anime","completed")
]

headers = {
    "Authorization": "Bearer " + access_token,
    "simkl-api-key": client_id
}

all_items = []

for media_type, status in endpoints:

    url = f"https://api.simkl.com/sync/all-items/{media_type}/{status}"
    result = make_request(url, headers)

    if not result:
        continue

    if isinstance(result, dict):
        result = list(result.values())[0]

    if not isinstance(result, list):
        continue

    for item in result:

        if media_type == "movies":
            obj = item.get("movie")
        else:
            obj = item.get("show")

        if not obj:
            continue

        ids = obj.get("ids", {})

        all_items.append({
            "title": obj.get("title"),
            "year": obj.get("year"),
            "imdb": ids.get("imdb"),
            "tmdb": ids.get("tmdb"),
            "type": media_type,
            "status": status
        })
make_csv(all_items)