import logging
import database as db
import os
import time


def run():
    try:
        logger.info("Run")
        while True:
            if EXIT:
                return

            downloads = database.getToDownloadLinks()  # [dict_keys(* from episode, * from link)]
            for link in downloads:
                # logger.debug("%s %s %s - adding to download" % (episode[0], episode[1], episode[2]))
                os.startfile(link['lin_link'])
                database.setDownloadingLinkAs(link['lin_id'], True)
                database.setDownloadEpisodeAs(link['ser_id'], link['epi_temporada'], link['epi_episodio'], False)
                if EXIT:
                    return
            time.sleep(5)
    finally:
        logger.debug("QUITTING DOWNLOAD RUN")


def finish():
    global EXIT
    EXIT = True
    logger.debug("EXIT COMMAND")


EXIT = False

logger = logging.getLogger("Program.{}".format(__name__))
database = db.Database()
