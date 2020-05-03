import logging
from scripts import TPB, KAT, utils, settings, database as db
import time
import datetime

DATETIME_FORMAT = settings.DATETIME_FORMAT


def run():
    logger.info("Run")
    while True:
        if EXIT:
            return
        failedintpb = 1
        failedinkat = 1
        episodes = database.getToDownloadEpisodeWithoutLink()  # [dict_keys(ser_id, ser_nome, epi_temporada, epi_episodio, epi_uatualizacao)]
        for episode in episodes:
            # print(episode, (datetime.datetime.now() - episode['epi_uatualizacao']), datetime.timedelta(hours=3) > (datetime.datetime.now() - episode['epi_uatualizacao']))
            if datetime.timedelta(hours=3) > (datetime.datetime.now() - datetime.datetime.strptime(episode['epi_uatualizacao'], DATETIME_FORMAT)):
                continue
            search_results = None
            searchtpb = None
            if failedintpb > 0 or (failedintpb <= 0 and failedinkat <= 0):
                searchtpb = tpb.fsearch(episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio'])
            if searchtpb is not None and len(searchtpb) > 0:
                failedintpb += 1
                logger.debug("Succeed TPB")
                search_results = searchtpb
            else:
                logger.debug("Failed TPB")
                failedintpb -= 1
                searchkat = kat.fsearch(episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio'])
                if searchkat is not None and len(searchkat) > 0:
                    failedinkat += 1
                    logger.debug("Succeed KAT")
                    search_results = searchkat
                else:
                    logger.debug("Failed KAT")
                    failedinkat -= 1
            if search_results:
                for match in search_results:
                    name1 = match['name']
                    name2 = f"{episode['ser_nome']} s{int(episode['epi_temporada']):02}e{int(episode['epi_episodio']):02}"
                    if utils.match(name1=name1, name2=name2):
                        database.addLink(episode['ser_id'], episode['epi_temporada'], episode['epi_episodio'], match['name'], match['magnet'])
                    else:
                        logger.debug(f"Link did not match episode: {name1} \t\t\t\t {name2}")

            if not database.setEpisodeUpdated(episode['ser_id'], episode['epi_temporada'], episode['epi_episodio']):
                logger.warning("%s %s %s - PROBLEM" % (episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio']))
                if EXIT:
                    return
        time.sleep(5)


def finish():
    global EXIT
    EXIT = True
    logger.info("Exitting")


EXIT = False

logger = logging.getLogger("Program.{}".format(__name__))
database = db.Database()
tpb = TPB.TPB()
kat = KAT.KAT()
