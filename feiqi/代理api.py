import urllib.request
import requests


def getip():
    r = requests.get("")
    new_data={"http" : r.text}
    return new_data


# print(getip())
