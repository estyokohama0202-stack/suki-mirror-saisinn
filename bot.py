import requests
import time
import json
import os

URL = "https://suki-kira.com/people/result/DJ%20SHIGE"
API = "https://suki-kira.com/api/comment/list"

with open("config.json") as f:
    config = json.load(f)

WEBHOOK = config["discord_webhook"]
TARGET = config["target"]

SAVE_FILE = "last_comment.json"


def load_last():
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE) as f:
        return json.load(f)


def save_last(comment_id):

    with open(SAVE_FILE, "w") as f:
        json.dump(comment_id, f)


def get_comments():

    page = 1
    comments = []

    while True:

        payload = {
            "target": TARGET,
            "page": page
        }

        r = requests.post(API, json=payload)

        if r.status_code != 200:
            print("API error")
            break

        data = r.json()

        if not data["comments"]:
            break

        for c in data["comments"]:

            comments.append({
                "id": c["id"],
                "user": c["name"],
                "text": c["comment"],
                "date": c["created_at"]
            })

        page += 1

    return comments


def send_discord(comment):

    payload = {
        "embeds": [
            {
                "author": {
                    "name": comment["user"]
                },
                "description": comment["text"][:2000],
                "color": 16711680,
                "footer": {
                    "text": "好き嫌い.com"
                },
                "url": URL
            }
        ]
    }

    requests.post(WEBHOOK, json=payload)


def main():

    last_id = load_last()

    comments = get_comments()

    newest = last_id

    for comment in reversed(comments):

        if last_id and comment["id"] == last_id:
            break

        send_discord(comment)

        newest = comment["id"]

        time.sleep(1)

    if newest:
        save_last(newest)


print("BOT START")

while True:

    try:
        main()
    except Exception as e:
        print("error", e)

    time.sleep(600)
