import logging
import threading
import settings
import database

logger = logging.getLogger("Program")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log_debug.log', mode=("a" if not settings.DEVELOMENT_MODE else "w"))
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s :: %(message)s'))
logger.addHandler(fh)

fh = logging.FileHandler('log_info.log', mode=("a" if not settings.DEVELOMENT_MODE else "w"))
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s :: %(message)s'))
logger.addHandler(fh)

fh = logging.FileHandler('log_warning.log', mode=("a" if not settings.DEVELOMENT_MODE else "w"))
fh.setLevel(logging.WARNING)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s :: %(message)s'))
logger.addHandler(fh)

fh = logging.FileHandler('log_error.log', mode=("a" if not settings.DEVELOMENT_MODE else "w"))
fh.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s :: %(message)s'))
logger.addHandler(fh)

fh = logging.FileHandler('log_critical.log', mode=("a" if not settings.DEVELOMENT_MODE else "w"))
fh.setLevel(logging.CRITICAL)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s :: %(message)s'))
logger.addHandler(fh)

logger.debug("*" * 50)
logger.debug("*" * 50)
logger.debug("Initiated")
logger.debug("*" * 50)
logger.debug("*" * 50)
logger.debug("Importing modules")

if settings.DEVELOMENT_MODE:
    logger.warning("-" * 50)
    logger.warning("-" * 50)
    logger.warning("USING: '{database}'".format(**settings.DATABASE))
    logger.warning("DEVELOPMENT: '{}'".format(settings.DEVELOMENT_MODE))
    logger.warning("-" * 50)
    logger.warning("-" * 50)

logger.debug("Modules imported")

if __name__ == '__main__':
    try:
        logger.debug("CREATING TABLES")
        db = database.Database(autoLoad=False)
        db.create_tables()

        import addEpisodes
        import download
        import updateLinks
        import user

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
