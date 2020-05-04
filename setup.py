import logging
import os
import requests
import sys
import json

# --------------------------------------------------------------------------------------
# DEFINITIONS
# github
GITHUB_TOKEN = "b30a3c77f56f8c39047b00f1aa232bf6ddcd3e2a"
OWNER = "alexregazzo"
REPO_NAME = "Downloader"
BRANCH_NAME = "master"
INSTALL_DIRPATH = "."

# log
INSTALLATION_LOG_DIRPATH = "."
LOG_FORMAT = "%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s  %(lineno)d :: %(message)s"
# updates
UPDATE_NONE = 0
UPDATE_PATCH_OR_BUG_FIX = 1
UPDATE_MINOR = 2
UPDATE_MAJOR = 3


# --------------------------------------------------------------------------------------


def _install(logger, userdata=None):
    # import github, install if necessary
    if userdata is None:
        userdata = {}
    logger.debug("Importing github")
    try:
        from github import Github
    except ModuleNotFoundError:
        logger.debug("Importing failed, module not found, installing")
        os.system("pip install PyGithub")
        logger.debug("Installed")
        logger.debug("Importing github again")
        from github import Github
        logger.debug("Imported")
    try:
        with open("version.json") as f:
            userdata.update(json.load(f))
    except:
        pass
    # connect to github
    print("Connecting...")
    logger.debug("Connect to github")
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(f"{OWNER}/{REPO_NAME}")

    # download files
    logger.debug("Download starting")
    contents = repo.get_contents("", BRANCH_NAME)
    print("Downloading...")
    version_file_path = None
    memory_content = {}
    while len(contents) > 0:
        content_file = contents.pop(0)
        logger.debug("Trying %s" % content_file.name)
        if content_file.type == "dir":
            logger.debug("Is folder: expanding")
            contents.extend(repo.get_contents(content_file.path, BRANCH_NAME))
            logger.debug("Expanded")
        else:
            path = os.path.join(INSTALL_DIRPATH, content_file.path)
            directory, _ = os.path.split(path)
            os.makedirs(directory, exist_ok=True)
            logger.debug("Download content")
            print("Downloading %s" % content_file.name)
            for _ in range(3):
                response = requests.get(content_file.download_url)
                if response.status_code == 200:
                    logger.debug("Request success")
                    if content_file.name == "version.json":
                        version_file_path = os.path.join(INSTALL_DIRPATH, content_file.path)
                        userdata.update(json.loads(response.text))
                        logger.debug("Found version file")
                        break
                    logger.debug("Write to memory")
                    memory_content[path] = response.text
                    logger.debug("Write success on %s" % path)
                    break
                else:
                    print("Error, retrying")
                    logger.warning("Request error on file %s" % path)
            else:
                print("Failed on file %s" % content_file.path)
                print("Operation cancelled!")
                logger.critical("Error while downloading %s" % path)
                os.system("pause")
                sys.exit(1)
    logger.debug("All files done writting to memory")
    logger.debug("Write to disk")
    print("Writting to disk")
    try:
        for path, content in memory_content.items():
            print(f"Writting {path}")
            logger.debug(f"Writting {path}")
            with open(path, "w", encoding="utf8") as f:
                f.write(content)
            logger.debug("Done")
    except:
        print("Something went wrong while installing")
        logger.exception("An exception ocurred while wirtting to disk")
        os.system("pause")
        sys.exit(1)

    # installing modules
    logger.debug("Installing modules")
    print("Installing modules")
    os.system("pip install -r requirements.txt")
    print("Finish installing modules")
    logger.debug("Finished installing modules")
    if version_file_path is None:
        logger.critical("Version file not found")
        logger.warning("Quitting!")
        print("An error ocurred")
        os.system("pause")
        sys.exit(1)
    logger.debug("Download finished")

    logger.debug("Writing version file")
    with open(version_file_path, "w", encoding="utf8") as f:
        json.dump(userdata, f)
    logger.debug("Writing done")


def install():
    # Initialize installation log
    os.makedirs(os.path.join(INSTALLATION_LOG_DIRPATH), exist_ok=True)
    logger = logging.getLogger("Setup")
    logger.setLevel(logging.DEBUG)

    for file_handler, level in [
        (logging.FileHandler(os.path.join(INSTALLATION_LOG_DIRPATH, 'installation.log'), mode="w"), logging.DEBUG)
    ]:
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
    logger.debug("-" * 50)
    logger.debug("Installation")

    # User Data save
    userdata = {}
    try:
        # show whats needed and confirm
        print("Welcome to Downloader setup")
        print("You need to have:")
        print("\t- utorrent installed on your machine")
        print("\t- API KEY from The Movie Database (https://www.themoviedb.org/)")
        print("\t- Some python modules (installed on this setup)")
        print("Notice: the program files will be located in the same folder of this setup")
        if input("Would you like to continue?[y/n]").lower() != "y":
            logger.debug("Quit by user")
            print("Quitting...")
            os.system("pause")
            sys.exit(0)
        logger.debug("Starting")
        print("Starting...")

        # user database setup
        logger.debug("Setup database started")
        userdata.update(
            {
                "TMDB": {
                    "TMDB_KEY": input("Insert the API key from The Movie Database: ")
                }
            })
        _install(logger, userdata)
        logger.debug("Finished installation")
        print("Installation finished successfully")
        os.system("pause")
        sys.exit(0)

    except Exception as e:
        logger.exception("Non expected exception ocurred")
        print("An error ocurred during installation, rerun or contact the developer.")
        print(e)
        os.system("pause")


def check_update():
    """
    Compare installed version with remote version to check if there are updates
    :return: # dict_keys("LOCAL_VERSION", "REMOTE_VERSION", "UPDATE_CODE")
    UPDATE_CODE: UPDATE_* definition based on the available update
    """
    result = {
        "LOCAL_VERSION": None,
        "REMOTE_VERSION": None,
        "UPDATE_CODE": UPDATE_NONE
    }
    logger = logging.getLogger("Program.{}".format("check_update"))
    try:
        # Get local installed version
        with open("version.json") as f:
            version = json.load(f)
        local_version = version["version"]
        result["LOCAL_VERSION"] = local_version
        logger.debug("Local version found: %s" % local_version)
        # Get remote version

        from github import Github

        github = Github(GITHUB_TOKEN)
        repo = github.get_repo(f"{OWNER}/{REPO_NAME}")
        remote_version_data = None
        try:
            content_file = repo.get_contents("version.json", BRANCH_NAME)
            response = requests.get(content_file.download_url)
            if response.status_code == 200:
                remote_version_data = json.loads(response.text)
        except:
            logger.exception("Unexpected exception ocurred while trying to get version file from github")
            return result

        if remote_version_data is None:
            logger.critical("Could not get version file")
            return result
        remote_version = remote_version_data['version']
        result["REMOTE_VERSION"] = remote_version
        logger.debug("Remote version found: %s" % remote_version)
        # compare versions
        # version: X.Y.Z
        # X - major
        # Y - minor
        # Z - Bugfix / patch

        for k, (lv, rv) in enumerate(zip(local_version.split("."), remote_version.split("."))):
            lv = int(lv)
            rv = int(rv)
            if rv > lv:
                if k == 0:  # major
                    logger.debug("Major update")
                    result["UPDATE_CODE"] = UPDATE_MAJOR
                    return result
                elif k == 1:  # minor
                    logger.debug("Minor update")
                    result["UPDATE_CODE"] = UPDATE_MINOR
                    return result
                elif k == 2:  # patch/bugfix
                    logger.debug("Patch/bugfix update")
                    result["UPDATE_CODE"] = UPDATE_PATCH_OR_BUG_FIX
                    return result
                else:
                    raise NotImplementedError("Something went wrong on versions comparisons comparison - local: %s, remote: %s" % (local_version, remote_version))
        logger.debug("No update")
    except:
        logger.exception("An exception ocurred while trying to execute check updates")
    return result


def update():
    logger = logging.getLogger("Program.{}".format("update"))
    logger.debug("Updating")
    try:

        _install(logger)
        logger.debug("Finished updating")
        print("Updating finished successfully")
        print("Reopen main to continue")
        os.system("pause")
        return
    except:
        logger.exception("An unexpeced error ocurred while trying to update")


if __name__ == "__main__":
    install()
