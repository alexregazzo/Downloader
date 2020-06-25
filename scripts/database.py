import logging
import datetime
from scripts import settings
import sqlite3
import threading
import os

DATABASE_NAME = "data.db"
DATABASE_DIR = settings.ABSOLUTE_PATHS['DATABASE_DIRPATH']
DATETIME_FORMAT = settings.DATETIME_FORMAT
SQL_NAME = "tables.sql"
SQL_PATH = os.path.join(settings.ABSOLUTE_PATHS['SQL_DIRPATH'], SQL_NAME)


class Database:
    logger = logging.getLogger("Program.{}".format(__name__))
    lock = threading.RLock()
    with lock:
        conn = sqlite3.connect(os.path.join(DATABASE_DIR, DATABASE_NAME), check_same_thread=False)
        conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])

    def __init__(self):
        self.logger.info("Database initiated!")
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        with open(SQL_PATH) as f:
            self.cursor.executescript(f.read())
        self.conn.commit()

    def insert(self, query):
        with self.lock:
            try:
                self.cursor.execute(query)
            except:
                self.logger.exception("An exception ocurred while inserting an object", stack_info=True)
                self.logger.critical("QUERY: %s" % query)
                return False
            else:
                return True
            finally:
                self.conn.commit()

    def select(self, query):
        with self.lock:
            try:
                self.cursor.execute(query)
            except:
                self.logger.exception("An exception ocurred while selecting")
                return []
            else:
                return self.cursor.fetchall()
            finally:
                self.conn.commit()

    def delete(self, query):
        with self.lock:
            try:
                self.cursor.execute(query)
            except:
                self.logger.exception("An exception ocurred while deleting")
                self.logger.critical("QUERY: %s" % query)
                return False
            else:
                return True
            finally:
                self.conn.commit()

    def update(self, query):
        with self.lock:
            try:
                self.cursor.execute(query)
            except:
                self.logger.exception("An exception ocurred while updating")
                self.logger.critical("QUERY: %s" % query)
                return False
            else:
                return True
            finally:
                self.conn.commit()

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    #           Serie SELECT
    # -----------------------------------------------------------------------------------
    def getToUpdateSeries(self, hours=3) -> [dict]:
        """
        Get series that weren't updated in the last 3 (default) hours
        :return: [dict_keys(ser_id), ... ]
        """
        QUERY = "SELECT ser_id FROM serie WHERE ser_uatualizado <= '%s'" % (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime(DATETIME_FORMAT)
        return self.select(QUERY)

    def getAllSeries(self) -> [dict]:
        """
        Get all series
        :return: [dict_keys(* from serie)]
        """
        QUERY = "SELECT * FROM serie"
        return self.select(QUERY)

    def getMinMaxSizeOfSerieNames(self) -> ((int, int) or None):
        """
        :return: (min, max) corresponding to the length of all the names
        :return: None if an error occurs
        """
        QUERY = "SELECT ser_nome FROM serie"
        names = [serie['ser_nome'] for serie in self.select(QUERY)]
        if len(names) == 0:
            return None
        minimum = len(names[0][0])
        maximum = len(names[0][0])
        for name in names:
            maximum = max(len(name), maximum)
            minimum = min(len(name), minimum)
        return minimum, maximum

    # -----------------------------------------------------------------------------------
    #           Serie INSERT
    # -----------------------------------------------------------------------------------

    def addSerie(self, ser_id, ser_nome) -> bool:
        """
        Add serie
        :return: whether the operation was performed sucessfully
        """
        ser_nome = ser_nome.replace("'", "")
        QUERY = f"INSERT INTO serie (ser_id, ser_nome, ser_adicionado) VALUES ('{ser_id}', '{ser_nome}', '{datetime.datetime.now().strftime(DATETIME_FORMAT)}')"
        return self.insert(QUERY)

    # -----------------------------------------------------------------------------------
    #           Serie UPDATE
    # -----------------------------------------------------------------------------------
    def setSerieUpdated(self, ser_id) -> bool:
        """
        Set serie as updated with curernt time
        :return: whether the operation was performed sucessfully
        """
        QUERY = f"UPDATE serie SET ser_uatualizado = '{datetime.datetime.now().strftime(DATETIME_FORMAT)}', ser_firstadd = 0 WHERE ser_id = '{ser_id}'"
        return self.update(QUERY)

    # -----------------------------------------------------------------------------------
    #           Serie DELETE
    # -----------------------------------------------------------------------------------
    def removeSerie(self, ser_id: int) -> bool:
        """
        Delete serie and all its episodes and links
        :return: whether the operation was performed sucessfully
        """
        QUERY1 = f"DELETE FROM link WHERE ser_id = '{ser_id}'"
        QUERY2 = f"DELETE FROM episodio WHERE ser_id = '{ser_id}'"
        QUERY3 = f"DELETE FROM serie WHERE ser_id = '{ser_id}'"
        return self.delete(QUERY1) and self.delete(QUERY2) and self.delete(QUERY3)

    # -----------------------------------------------------------------------------------
    #           Episodio SELECT
    # -----------------------------------------------------------------------------------
    def getToDownloadEpisodeWithoutLink(self) -> [dict]:
        """
        Get all episodes that should be downloaded and don't have any link
        :return: [dict_keys(ser_id, ser_nome, epi_temporada, epi_episodio, epi_uatualizacao)]
        """
        QUERY = "SELECT s.ser_id, s.ser_nome, e.epi_temporada, e.epi_episodio, e.epi_uatualizacao FROM episodio AS e NATURAL JOIN serie AS s LEFT JOIN link AS l ON e.ser_id = l.ser_id AND e.epi_temporada = l.epi_temporada AND e.epi_episodio = l.epi_episodio WHERE e.epi_baixar = 1;"
        return self.select(QUERY)

    def getToDownloadEpisode(self) -> [dict]:
        """
        Get all episodes that should be downloaded whether there is a link or not
        :return: [dict_keys(ser_id, ser_nome, epi_temporada, epi_episodio)]
                """
        QUERY = "SELECT s.ser_id, s.ser_nome, e.epi_temporada, e.epi_episodio FROM episodio AS e NATURAL JOIN serie AS s WHERE e.epi_baixar = 1"
        return self.select(QUERY)

    def getAllEpisodes(self) -> [dict]:
        """
        Get all episodes in database
        :return: [dict_keys(ser_id, epi_temporada, epi_episodio), ... ]
        """
        QUERY = "SELECT ser_id, epi_temporada, epi_episodio FROM episodio"
        return self.select(QUERY)

    def getRecentlyAddedEpisodes(self, hours=3) -> [dict]:
        """
        Get all episodes added in the last 3 (default) hours, ordered by most recent to least recent
        :return: [dict_keys(ser_nome, epi_temporada, epi_episodio, epi_adicionado), ... ]
        """
        QUERY = "SELECT ser_nome, epi_temporada, epi_episodio, epi_adicionado FROM episodio JOIN serie WHERE epi_adicionado > '%s' ORDER BY epi_adicionado DESC" % (
                datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime(DATETIME_FORMAT)
        return self.select(QUERY)

    def getLastAddedEpisodes(self, amount=10) -> [dict]:
        """
        Get the 10 (default) last added episodes ordered by most recent to leas recent
        :return: [dict_keys(ser_nome, epi_temporada, epi_episodio, epi_adicionado), ... ]
        """
        QUERY = f"SELECT ser_nome, epi_temporada, epi_episodio, epi_adicionado FROM episodio JOIN serie ORDER BY epi_adicionado DESC LIMIT {amount}"
        return self.select(QUERY)

    def getEpisode(self, ser_id, epi_temporada, epi_episodio) -> (dict or None):
        """
        Get episode that matches ser_id, epi_temporada, epi_episode
        :return: dict_keys(ser_id, epi_temporada, epi_episodio) or None if it doesn't exist
        """
        QUERY = f"SELECT ser_id, epi_temporada, epi_episodio FROM episodio WHERE ser_id = '{ser_id}' AND epi_temporada='{epi_temporada}' AND epi_episodio = '{epi_episodio}'"
        return self.select(QUERY)

    # -----------------------------------------------------------------------------------
    #           Episodio INSERT
    # -----------------------------------------------------------------------------------
    def addEpisode(self, ser_id, epi_temporada, epi_episodio, epi_lancamento) -> bool:
        """
        Add episode to database
        :return: whether the operation was performed sucessfully
        """
        QUERY = f"INSERT INTO episodio (ser_id, epi_temporada, epi_episodio, epi_lancamento, epi_baixar, epi_adicionado) VALUES ('{ser_id}', '{epi_temporada}', '{epi_episodio}', '{epi_lancamento}',  (SELECT not ser_firstadd FROM serie WHERE ser_id = '{ser_id}'), '{datetime.datetime.now().strftime(DATETIME_FORMAT)}')"
        return self.insert(QUERY)

    # -----------------------------------------------------------------------------------
    #           Episodio UPDATE
    # -----------------------------------------------------------------------------------
    def setDownloadEpisodeAs(self, ser_id, epi_temporada, epi_episodio, epi_baixar) -> bool:
        """
        Set episode epi_baixar as true or false
        :return: whether the operation was performed sucessfully
        """
        epi_baixar = 1 if epi_baixar else 0
        QUERY = f"UPDATE episodio SET epi_baixar='{epi_baixar}' WHERE ser_id='{ser_id}' AND epi_temporada='{epi_temporada}' AND epi_episodio='{epi_episodio}'"
        return self.update(QUERY)

    def setEpisodeUpdated(self, ser_id, epi_temporada, epi_episodio) -> bool:
        """
        Set episode as updated with the current time
        :return: whether the operation was performed sucessfully
        """
        QUERY = f"UPDATE episodio SET epi_uatualizacao = '{datetime.datetime.now().strftime(DATETIME_FORMAT)}' WHERE ser_id = '{ser_id}' AND epi_temporada = '{epi_temporada}' AND epi_episodio = '{epi_episodio}'"
        return self.update(QUERY)

    def setToDownloadAfterEpisodeAs(self, ser_id, epi_temporada, epi_episodio, epi_baixar: bool) -> bool:
        """
        Set all episodes after specified episode to download
        :return: whether the operation was performed sucessfully
        """
        # set to download all after an episode (includes episode selected)
        epi_baixar = 1 if epi_baixar else 0
        QUERY = f"UPDATE episodio SET epi_baixar = {epi_baixar} WHERE ser_id = '{ser_id}' AND (epi_temporada > '{epi_temporada}' OR (epi_temporada = '{epi_temporada}' AND epi_episodio >= '{epi_episodio}'));"
        return self.update(QUERY)

    def setToDownloadEpisodio(self, ser_id, epi_temporada, epi_episodio):
        """
        Set specified episode to download
        :return: whether the operation was performed sucessfully
        """
        print("ERROR")
        QUERY = f"UPDATE episodio SET epi_baixar = 1 WHERE ser_id = '{ser_id}' AND epi_temporada = '{epi_temporada}' AND epi_episodio = '{epi_episodio}';"
        return self.update(QUERY)

    # -----------------------------------------------------------------------------------
    #           Link SELECT
    # -----------------------------------------------------------------------------------
    def getToDownloadLinks(self):
        """
        Get all episodes that are supposed to be downloaded and has a link
        :return: [dict_keys(* from episode, * from link)]
        """
        QUERY = "SELECT * FROM episodio AS e NATURAL JOIN link WHERE e.epi_baixar = 1 AND link.lin_baixando = 0 GROUP BY ser_id, epi_temporada, epi_episodio;"
        return self.select(QUERY)

    # -----------------------------------------------------------------------------------
    #           Link INSERT
    # -----------------------------------------------------------------------------------
    def addLink(self, ser_id, epi_temporada, epi_episodio, lin_nome, lin_link) -> bool:
        """
        Add link to link to database
        :return: whether the operation was performed sucessfully
        """
        QUERY = f"INSERT INTO link (ser_id, epi_temporada, epi_episodio, lin_nome, lin_link, lin_adicionado) VALUES ('{ser_id}', '{epi_temporada}', '{epi_episodio}', '{lin_nome}', '{lin_link}', '{datetime.datetime.now().strftime(DATETIME_FORMAT)}')"
        return self.insert(QUERY)

    # -----------------------------------------------------------------------------------
    #           Link UPDATE
    # -----------------------------------------------------------------------------------
    def setDownloadingLinkAs(self, lin_id, lin_baixando) -> bool:
        """
        Update link settings lin_baixando as True or False
        :return: whether the operation was performed sucessfully
        """
        lin_baixando = 1 if lin_baixando else 0
        QUERY = f"UPDATE link SET lin_baixando = '{lin_baixando}' WHERE lin_id = '{lin_id}'"
        return self.update(QUERY)

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
    # db = Database()setToUnDownloadAfterEpisode
    # print(db.getToDownloadEpisodeWithoutLink())
