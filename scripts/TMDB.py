import os
import threading
import time
from hashlib import md5 as hashing
from scripts.TMDBSearch import *
import logging


class TMDB:
    def __init__(self, caching=True):
        self.logger = logging.getLogger("Program.%s" % __name__)
        self.logger.debug("Object created")
        self._cache = caching
        self._path = "cache/TMDBCache.json"
        self._data = None
        self._fileChecker()
        self.lock = threading.RLock()

    @staticmethod
    def _validateDate(a: float, b: float, limit: float = 10800):
        """
        :param a: [seconds]
        :param b: [seconds]
        :param limit: default is set to 3 hours [seconds]
        :return: True if difference is greater than limit else False
        """
        return abs(a - b) < limit

    def _save(self):
        self._fileChecker()
        with open(self._path, "w") as f:
            json.dump(self._data, f)

    def _fileChecker(self):
        """
        create the cache file if it does not exist
        put {} in file if it's empty
        """
        if not os.path.isdir(os.path.dirname(self._path)):
            os.mkdir(os.path.dirname(self._path))
        if os.path.isfile(self._path):
            if os.path.getsize(self._path) == 0:
                with open(self._path, "w") as f:
                    f.write("{}")
                    f.close()
        else:
            with open(self._path, "w+") as f:
                f.write("{}")
                f.close()

    def _loadCache(self):
        """
        loads data from cache file
        """
        self._fileChecker()
        if self._data is None:
            with open(self._path) as f:
                try:
                    self._data = json.load(f)
                except Exception as e:
                    self.logger.warning("Error while loading TPB cache\n\n%s" % e)
                    self._data = {}

    def _get(self, tp: str, *args, getAnyway: bool = False):
        self._loadCache()
        key = hashing((str(tp) + ":" + ",".join(str(i) for i in args)).encode('utf-8')).hexdigest()
        if tp not in self._data:
            return None
        else:
            if key in self._data[tp]:
                if getAnyway:
                    return self._data[tp][key]['data']
                if self._validateDate(self._data[tp][key]['date'], time.time()):
                    return self._data[tp][key]['data']
                else:
                    # del self._data[tp][key]
                    # self._save()
                    return True
            else:
                return False

    def _addToCache(self, tp: str, data: dict, *args):
        self._loadCache()
        key = hashing((str(tp) + ":" + ",".join(str(i) for i in args)).encode('utf-8')).hexdigest()
        if tp not in self._data:
            self._data[tp] = {key: {"date": time.time(), "data": data}}
        else:
            self._data[tp][key] = {"date": time.time(), "data": data}
        self._save()

    def searchTVShow(self, **kwargs):
        """
        use 'name' to search for series names
        use 'id' to get serie from id
        use 'id' 'season' to get season from serie
        use 'id' 'season' 'episode' to get episode from season, serie
        :return: all the information from the TMDB
        """

        ans = None
        if "id" in kwargs:
            if "season" in kwargs:
                if "episode" in kwargs:
                    # episode type of search
                    if self._cache:
                        ans = self._get("episode", kwargs['id'], kwargs['season'], kwargs['episode'])
                        if type(ans) is dict:
                            return ans
                    ans = TMDBSearch().Episode(kwargs['id'], kwargs['season'], kwargs['episode'])
                    if ans is not None:
                        self._addToCache("episode", ans, kwargs['id'], kwargs['season'], kwargs['episode'])
                        self._save()
                        return ans
                    elif self._cache:
                        ans = self._get("episode", kwargs['id'], kwargs['season'], kwargs['episode'], getAnyway=True)
                else:
                    # season type of search
                    if self._cache:
                        ans = self._get("season", kwargs['id'], kwargs['season'])
                        if type(ans) is dict:
                            return ans
                    ans = TMDBSearch().Season(kwargs['id'], kwargs['season'])
                    if ans is not None:
                        self._addToCache("season", ans, kwargs['id'], kwargs['season'])
                        self._save()
                        return ans
                    elif self._cache:
                        ans = self._get("season", kwargs['id'], kwargs['season'], getAnyway=True)
            else:
                # tvshow through id type of search
                if self._cache:
                    ans = self._get("tvshowid", kwargs['id'])
                    if type(ans) is dict:
                        return ans
                ans = TMDBSearch().TVShow(kwargs['id'])
                if ans is not None:
                    self._addToCache("tvshowid", ans, kwargs['id'])
                    self._save()
                    return ans
                elif self._cache:
                    ans = self._get("tvshowid", kwargs['id'], getAnyway=True)

        elif "name" in kwargs:
            # tvshow type of search
            if self._cache:
                ans = self._get("tvshow", kwargs['name'])
                if type(ans) is dict:
                    return ans
            ans = TMDBSearch().SearchTVShow(kwargs['name'])
            if ans is not None:
                self._addToCache("tvshow", ans, kwargs['name'])
                self._save()
                return ans
            elif self._cache:
                ans = self._get("tvshow", kwargs['name'], getAnyway=True)
        else:
            print("Type could not be defined")
            print("Args passed: {}".format(kwargs))
        return ans

# search = TMDB()
# print(search.searchTVShow(name="the blacklistibibibubib"))
# print(search.searchTVShow(id=46952561651))
# print(search.searchTVShow(id=46952, season=30))
# print(search.searchTVShow(id=46952, season=3, episode=50))
