from urllib.parse import quote
import re
import json
import os
import time
import logging
import requests
from bs4 import BeautifulSoup


class TPB:
    def __init__(self, caching=True, attempts=3):
        self.logger = logging.getLogger("Program.%s" % __name__)
        self.logger.debug("Object created")
        self._path = "cache/TPBCache.json"
        self.attempts = attempts
        self._cache = caching
        self._data = None
        self.URL = "https://thepiratebay.org/search/{qry}/0/99/0"
        self.REGEX = re.compile(r'<a href="(magnet:\?xt=urn:btih:.*?&dn=(.*?)&.*?)"', re.IGNORECASE)
        self._invalidRaws = ["Database maintenance, please check back in 10 minutes. 12", "Bad gateway", "Connection timed out"]
        self._fileChecker()

    def _validateWeb(self, s: str):
        """
        :param s: web raw
        :return: return True if s is valid (not database maintance or errors)
        """
        for k, string in enumerate(self._invalidRaws):
            if string in s:
                # print("Invalidation code: {}".format(k))

                return False
        return True

    @staticmethod
    def _validateDate(a: float, b: float, limit: float = 10800):
        """
        :param a: [seconds]
        :param b: [seconds]
        :param limit: default is set to 3 hours [seconds]
        :return: True if difference is greater than limit else False
        """
        return abs(a - b) < limit

    def _parse(self, raw):
        """
        :param raw: parse data from website to list of magnets and names
        :return: [dict_keys(position, name, magnet, seeders), ...]
        """
        # k = 0
        # while os.path.exists(f"responses/try{k}.html"):
        #     k += 1
        # with open(f"responses/trytpb{k}.html", "w") as f:
        #     f.write(raw)

        results = []
        soup = BeautifulSoup(raw, "lxml")

        try:
            for k, tr in enumerate(soup.body.table.find_all('tr', recursive=False)):
                td1, td2 = tr.find_all('td', recursive=False)[1:3]
                results.append(
                    {
                        "position": k,
                        "name": td1.div.text,
                        "magnet": td1.find('a', recursive=False).get('href'),
                        "seeders": int(td2.text)
                    })
        except:
            raise
        return results

    def _save(self):
        self._fileChecker()
        with open(self._path, "w") as f:
            json.dump(self._data, f)

    def _search(self, query):
        """
        :param query: parsed string to search
        :return: None or [dict_keys(position, name, magnet, seeders), ...]
        """
        try:
            rawresults = requests.get(self.URL.format(qry=query), timeout=3).text
            # print(rawresults)
            # rawresults = urlopen(Request(self.URL.format(qry=query), headers={'User-Agent': 'Mozilla/5.0'}), cafile=certifi.where()).read().decode("UTF-8")
        except requests.exceptions.Timeout:
            self.logger.debug("TimedOut")
            return None
        except:
            self.logger.exception(query)
            return None
        else:
            if "No hits. Try adding an asterisk in you search phrase." in rawresults:
                return []
            if not self._validateWeb(rawresults):
                return None
            ans = self._parse(rawresults)  # [dict_keys(position, name, magnet, seeders), ...]
            if len(ans) > 0:
                self._loadCache()
                self._data[query] = {"date": time.time(), "data": ans}
                self._save()
                return ans
            return None

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

    def _get(self, query, getAnyway: bool = False):
        """
        :param query: parsed string to search
        :return: data from cache if it exists and it's valid, otherwise return None
        """
        self._loadCache()
        if query in self._data:
            if getAnyway:
                return self._data[query]['data']
            if self._validateDate(self._data[query]['date'], time.time()):
                return self._data[query]['data']
            else:
                pass
                # del self._data[query]
                # self._save()
        return None

    def search(self, q):
        """
        :param q: unparsed query
        :return: None or [dict_keys(position, name, magnet, seeders), ...]
        """
        q = quote(q)
        for c in range(self.attempts):
            if self._cache:
                ans = self._get(q)
                if ans is None:
                    ans = self._search(q)  # None or [dict_keys(position, name, magnet, seeders), ...]
                    # can be logged
            else:
                ans = self._search(q)  # None or [dict_keys(position, name, magnet, seeders), ...]
            if ans is not None:
                return ans
                # print("Attempt", c + 1)
        return self._get(q, getAnyway=True)

    def fsearch(self, name, season, episode):
        name = name.replace("'", "")
        return self.search("{} s{:0>2d}e{:0>2d}".format(name, season, episode))  # None or [dict_keys(position, name, magnet, seeders), ...]


if __name__ == "__main__":
    s = TPB(caching=False)
    print(s.fsearch("the blacklist", 3, 7)[:])
