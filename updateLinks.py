import logging
import database as db
import TPB
import KAT
import time
import datetime


def do_search_on_tpb():
    pass


def do_search_on_kat():
    pass


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
            if datetime.timedelta(hours=3) > (datetime.datetime.now() - episode['epi_uatualizacao']):
                continue
            searchtpb = None
            if failedintpb > 0 or (failedintpb <= 0 and failedinkat <= 0):
                searchtpb = tpb.fsearch(episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio'])
            if searchtpb is not None and len(searchtpb) > 0:
                failedintpb += 1
                logger.debug("Succeed TPB")
                for match in searchtpb:
                    database.addLink(episode['ser_id'], episode['epi_temporada'], episode['epi_episodio'], match['name'], match['magnet'], match['seeders'])
            else:
                logger.debug("Failed TPB")
                failedintpb -= 1
                searchkat = kat.fsearch(episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio'])
                if searchkat is not None and len(searchkat) > 0:
                    failedinkat += 1
                    logger.debug("Succeed KAT")
                    for match in searchkat:
                        database.addLink(episode['ser_id'], episode['epi_temporada'], episode['epi_episodio'], match['name'], match['magnet'], match['seeders'])
                else:
                    logger.debug("Failed KAT")
                    failedinkat -= 1
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
