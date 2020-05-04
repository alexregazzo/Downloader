import logging
import threading
import os
import sys
import json
from scripts import settings
import setup

LOG_FORMAT = settings.LOG_FORMAT
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

try:
    with open("version.json") as f:
        VERSION = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    print("Something is wrong with your installation")
    print("Please run setup or contact developers")
    os.system("pause")
    sys.exit(1)

# CHECK UPDATES
logger.debug("Check updates")
update = setup.check_update()  # dict_keys("LOCAL_VERSION", "REMOTE_VERSION", "UPDATE_CODE")
if update["UPDATE_CODE"] != setup.UPDATE_NONE:
    # Update available
    if update['UPDATE_CODE'] == setup.UPDATE_MAJOR:
        print("There is a MAJOR update available")
    elif update['UPDATE_CODE'] == setup.UPDATE_MINOR:
        print("There is a MINOR update available")
    elif update['UPDATE_CODE'] == setup.UPDATE_PATCH_OR_BUG_FIX:
        print("There is a bug fix or patch update available")
    if input(f"""Would you like to update{f" from {update['LOCAL_VERSION']}" if update['LOCAL_VERSION'] else ""}{f" to {update['REMOTE_VERSION']}" if update['REMOTE_VERSION'] else ""}? [y/n]""").lower() == "y":
        setup.update()
        sys.exit(0)

# INIT
logger.debug("Init")

if __name__ == '__main__':
    try:
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
