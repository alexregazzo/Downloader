import logging
import database as db
import TMDB
import time
import utils


def run():
    try:
        logger.info("Run")
        while True:
            if EXIT:
                return
            try:
                episodes = database.getAllEpisodes()  # (ser_id, epi_temporada, epi_episodio)
                tvshows = database.getToUpdateSeries()  # (ser_id)
                for tvshow in tvshows:
                    logger.debug("UPDATING %s" % tvshow["ser_id"])
                    tmdb.lock.acquire()
                    serie = tmdb.searchTVShow(id=tvshow["ser_id"])
                    tmdb.lock.release()
                    for season in serie['seasons']:
                        if season['season_number'] == 0:
                            continue
                        for episode in range(season['episode_count']):
                            ep = {"ser_id": tvshow["ser_id"], "epi_temporada": season['season_number'], "epi_episodio": episode + 1}
                            if not utils.dictInList(ep, episodes, keys_to_compare=['ser_id', 'epi_temporada', 'epi_episodio']):
                                tmdb.lock.acquire()
                                ep_tmdb = tmdb.searchTVShow(id=ep["ser_id"], season=ep["epi_temporada"], episode=ep["epi_episodio"])
                                tmdb.lock.release()
                                try:
                                    database.addEpisode(ep["ser_id"], ep["epi_temporada"], ep["epi_episodio"], ep_tmdb['air_date'])  # return bool
                                except:
                                    logger.debug(f"{ep} {ep_tmdb}")
                                    logger.exception(ep_tmdb)

                            if EXIT:
                                return
                    logger.debug("Serie updated: %s" % tvshow["ser_id"])
                    if not database.setSerieUpdated(tvshow["ser_id"]):
                        logger.warning("'%s' time not updated" % tvshow["ser_id"])
            except:
                logger.exception("An error ocurred")
            time.sleep(5)
    finally:
        logger.debug("QUITTING ADDEPISODES RUN")


def finish():
    global EXIT
    EXIT = True
    logger.debug("EXIT COMMAND")


EXIT = False
logger = logging.getLogger("Program.{}".format(__name__))
database = db.Database()
tmdb = TMDB.TMDB()
