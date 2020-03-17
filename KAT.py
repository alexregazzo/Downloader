import requests
from urllib.parse import quote
import json
import os
import time
import logging
from bs4 import BeautifulSoup


class KAT:
    def __init__(self, caching=True, attempts=3):
        self.logger = logging.getLogger("Program.%s" % __name__)
        self.logger.debug("Object created")
        self._path = "cache/KATCache.json"
        self.attempts = attempts
        self._cache = caching
        self._data = None
        self.URL = "https://katcr.co/katsearch/page/1/{qry}"
        self._invalidRaws = []
        self._invalidMagnets = ["https://www.get-express-vpn.com/torrent-vpn?offer=3monthsfree&a_fid=katcr"]
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
        :return: list of objects found
        """
        # k = 0
        # while os.path.exists(f"responses/try{k}.html"):
        #     k += 1
        # with open(f"responses/trykat{k}.html", "w") as f:
        #     f.write(raw)

        soup = BeautifulSoup(raw, "lxml")
        results = []
        try:
            for k, tr in enumerate(soup.body.table.tbody.find_all('tr', recursive=False)):
                tds = tr.find_all('td', recursive=False)
                divs = tds[0].div.find_all("div", recursive=False)
                name = divs[0].a.b.text
                magnet = divs[1].find_all('a', recursive=False)[2].get('href')
                results.append(
                    {
                        "position": k,
                        "name": name,
                        "magnet": magnet,
                        "seeders": int(tds[4].text)
                    })
        except:
            self.logger.exception("Exception ocurred while trying to parse data from KAT")
            return []
        else:
            return results

    def _save(self):
        self._fileChecker()
        with open(self._path, "w") as f:
            json.dump(self._data, f)

    def _search(self, query):
        """
        :param query: parsed string to search
        :return: returns data from website if it's valid, otherwise return None
        """
        try:
            response = requests.get(self.URL.format(qry=query), timeout=3)
            if response.status_code == 200:
                rawresults = response.text
            else:
                return None
        except requests.exceptions.Timeout:
            self.logger.debug("TimedOut")
            return None
        except:
            self.logger.exception(query)
            return None
        else:
            if not self._validateWeb(rawresults):
                return None
            ans = self._parse(rawresults)
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
        return None

    def search(self, q):
        """
        :param q: unparsed query
        :return: parsed data from search
        """
        q = quote(q)
        for c in range(self.attempts):
            if self._cache:
                ans = self._get(q)
                if ans is None:
                    ans = self._search(q)
                    # can be logged
            else:
                ans = self._search(q)
            if ans is not None:
                return ans
        return self._get(q, getAnyway=True)

    def fsearch(self, name, season, episode):
        name = name.replace("'", "")
        results = self.search("{} s{:0>2d}e{:0>2d}".format(name, season, episode))  # None or [dict_keys(position, name, magnet, seeders), ...]
        if results is not None:
            self.logger.debug("Filtering results")
            self.logger.debug(f"Before: {results}")
            results = list(filter(lambda result: (not any([invalidmagnet in result['magnet'] for invalidmagnet in self._invalidMagnets])) and any([namepart in result['name'] for namepart in name.split(" ")]), results))
            self.logger.debug(f"After: {results}")
        return results


if __name__ == "__main__":
    kat = KAT(caching=False)
    # kat = KAT(caching=True)
    print(kat.fsearch("élite", 3, 1))
