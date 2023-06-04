import json
import os

def read(asset):
    with open(asset+".json", "r", encoding="utf8") as read_file:
        data = json.load(read_file)

    return data