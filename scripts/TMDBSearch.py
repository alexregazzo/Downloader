import requests
from urllib.parse import quote
import json
from scripts import settings
import os

VERSION_DIRPATH = settings.ABSOLUTE_PATHS['VERSION_DIRPATH']
VERSION_PATH = os.path.join(VERSION_DIRPATH, "version.json")


class TMDBSearch:
    def __init__(self):
        with open(VERSION_PATH) as f:
            tmdb_data = json.load(f)
        self.API_KEY = tmdb_data['TMDB_KEY']

    def SearchTVShow(self, query: str):
        request = requests.get('https://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(self.API_KEY, quote(query)))
        if request.ok:
            return request.json()
        return {}

    def TVShow(self, _id):
        try:
            request = requests.get('https://api.themoviedb.org/3/tv/{}?api_key={}'.format(_id, self.API_KEY))
        except requests.exceptions.ConnectionError:
            # print("Bad internet connection! Verify network!")
            pass
        else:
            if request.ok:
                return request.json()
            return {}
        return {}

    def Season(self, _id, _season):
        request = requests.get('https://api.themoviedb.org/3/tv/{}/season/{}?api_key={}'.format(_id, _season, self.API_KEY))
        if request.ok:
            return request.json()
        return {}

    def Episode(self, _id, _season, _episode):
        request = requests.get('https://api.themoviedb.org/3/tv/{}/season/{}/episode/{}?api_key={}'.format(_id, _season, _episode, self.API_KEY))
        if request.ok:
            return request.json()
        return {}
