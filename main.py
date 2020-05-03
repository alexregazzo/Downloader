import logging
import threading
import os
from scripts import settings, database

LOG_FORMAT = "%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s  %(lineno)d :: %(message)s"
logger = logging.getLogger("Program")
logger.setLevel(logging.DEBUG)
LOGGING_MODE = "a" if not settings.DEVELOMENT_MODE else "w"
LOGGING_DIRPATH = settings.ABSOLUTE_PATHS['LOGGING_DIRPATH']

fh = logging.FileHandler(os.path.join(LOGGING_DIRPATH, 'log_debug.log'), mode=LOGGING_MODE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)

fh = logging.FileHandler(os.path.join(LOGGING_DIRPATH, 'log_info.log'), mode=LOGGING_MODE)
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)

fh = logging.FileHandler(os.path.join(LOGGING_DIRPATH, 'log_warning.log'), mode=LOGGING_MODE)
fh.setLevel(logging.WARNING)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)

fh = logging.FileHandler(os.path.join(LOGGING_DIRPATH, 'log_error.log'), mode=LOGGING_MODE)
fh.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)

fh = logging.FileHandler(os.path.join(LOGGING_DIRPATH, 'log_critical.log'), mode=LOGGING_MODE)
fh.setLevel(logging.CRITICAL)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)

logger.debug("*" * 50)
logger.debug("*" * 50)
logger.debug("Initiated")
logger.debug("*" * 50)
logger.debug("*" * 50)
logger.debug("Importing modules")

logger.debug("Modules imported")

if __name__ == '__main__':
    try:
        logger.debug("CREATING TABLES")
        db = database.Database()
        db.create_tables()

        from scripts import download, addEpisodes, updateLinks, settings, database, user

        logger.debug("Starting threads")
        threading.Thread(target=addEpisodes.run).start()
        threading.Thread(target=download.run).start()
        threading.Thread(target=updateLinks.run).start()
        user = threading.Thread(target=user.run)

        user.start()
        logger.debug("Threads started")
        user.join()
        print("Tarefa do usuario finalizada...")
        print("Finalizando outras tarefas...")
        logger.debug("User thread joined")
        logger.debug("Finishing threads")
        addEpisodes.finish()
        download.finish()
        updateLinks.finish()
        logger.debug("Thread finished")
        activethreads = len(threading.enumerate())
        print("Finalizando %s tarefas" % activethreads)
        logger.debug("active threads: %s" % str(threading.enumerate()))
        while activethreads > 1:
            n = len(threading.enumerate())
            if n != activethreads:
                logger.debug("active threads: %s" % str(threading.enumerate()))
                print("Finalizando %s tarefas" % activethreads)
            activethreads = n
        print("Finalizado")

    except:
        logger.exception("An exception occurred!")
        raise
