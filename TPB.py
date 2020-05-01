from urllib.parse import quote
import logging
import requests
from bs4 import BeautifulSoup


class TPB:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("Program.%s" % __name__)
        self.url = "https://apibay.org/q.php?q={q}&cat="
        pass

    @staticmethod
    def _get_trackers():
        tr = '&tr=' + quote('udp://tracker.coppersurfer.tk:6969/announce')
        tr += '&tr=' + quote('udp://9.rarbg.to:2920/announce')
        tr += '&tr=' + quote('udp://tracker.opentrackr.org:1337')
        tr += '&tr=' + quote('udp://tracker.internetwarriors.net:1337/announce')
        tr += '&tr=' + quote('udp://tracker.leechers-paradise.org:6969/announce')
        tr += '&tr=' + quote('udp://tracker.coppersurfer.tk:6969/announce')
        tr += '&tr=' + quote('udp://tracker.pirateparty.gr:6969/announce')
        tr += '&tr=' + quote('udp://tracker.cyberia.is:6969/announce')
        return tr

    def _search(self, url):
        try:
            response = requests.get(url)
            if response.ok:
                torrents = response.json()
                results = []
                for k, torrent in enumerate(torrents):
                    info_hash = torrent['info_hash']
                    name = torrent['name']

                    magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={quote(name)}{quote(self._get_trackers())}"
                    # print(magnet)
                    torrent.update({
                        "position": k,
                        "magnet":magnet,
                        "seeders": int(torrent['seeders'])
                    })

                    results.append(torrent)
                self.logger.debug(f"TPB {len(results)} results found")
                return results
            return None
        except:
            self.logger.exception("Exception during search")
        return None

    def fsearch(self, name: str, season: int, episode: int):
        try:
            season = int(season)
            episode = int(episode)
            return self._search(self.url.format(q=quote(f"{name} s{season:02}e{episode:02}")))
        except:
            self.logger.exception("An exception ocurred while trying to get data from TPB")
        return None


if __name__ == "__main__":
    tpb = TPB()
    # print(tpb.fsearch("élite", 1, 2))
    # pass
    # print(len("magnet:?xt=urn:btih:394A4E4A0F35AEE986E5837605C7190F0E12BEEF&dn=The.Blacklist.S07E02.HDTV.x264-SVA%5Bettv%5D&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce"))