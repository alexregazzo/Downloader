import logging
import os
import requests
import sys
import json

# --------------------------------------------------------------------------------------
# DEFINITIONS
# github
GITHUB_TOKEN = "b30a3c77f56f8c39047b00f1aa232bf6ddcd3e2a"
REPO_NAME = "Downloader"
BRANCH_NAME = "organize"
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
        print("For the database you have 2 options:")
        print("\t- MySQLServer")
        print("\t\t+ Needs:")
        print("\t\t\t* Server installed")
        print("\t\t\t* Access to host, username, and password")
        print("\t- SQLITE3 (native python module)")
        print("Notice: the program files will be located in the same folder of this setup")
        if input("Would you like to continue?[y/n]").lower() != "y":
            logger.debug("Quit by user")
            print("Quitting...")
            os.system("pause")
            sys.exit(0)
        logger.debug("Starting")
        print("Starting...")
        # import github, install if necessary
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

        # connect to github
        print("Connecting...")
        logger.debug("Connect to github")
        github = Github(GITHUB_TOKEN)
        repo = github.get_repo("alexregazzo/%s" % REPO_NAME)

        # download files
        logger.debug("Download starting")
        contents = repo.get_contents("", BRANCH_NAME)
        print("Downloading...")
        version_file_path = None
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
                        logger.debug("Write")
                        with open(path, "w") as f:
                            f.write(response.text)
                        logger.debug("Write success on %s" % path)
                        break
                    else:
                        print("Error, retrying")
                        logger.warning("Request error on file %s" % path)
                else:
                    print("Failed on file %s" % content_file.path)
                    logger.critical("Error while downloading %s" % path)

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

        # user database setup
        logger.debug("Setup database started")
        userdata.update(
            {
                "TMDB": {
                    "TMDB_KEY": input("Insert the API key from The Movie Database: ")
                }
            })
        while True:
            try:
                print("Choose the type of database you'd like to use:")
                print("1 - MYSQLServer (advanced)")
                print("2 - SQLITE (recommended)")
                choice = int(input("Enter the number:"))
                if choice != 1 and choice != 2:
                    raise ValueError
            except ValueError:
                pass
            else:
                break
        if choice == 1:  # MYSQLSERVER
            logger.debug("MYSQLSERVER chosen")
            print("Setup MYSQLServer:")
            userdata.update(
                {
                    "DATABASE": {
                        "type": "mysqlserver",
                        "connection":
                            {
                                "host": input("Enter server host (ex: localhost): "),
                                "user": input("Enter user (ex: root): "),
                                "passwd": input("Enter password: "),
                                "database": "series"
                            }
                    }
                })
            # TODO: test mysqlserver
        elif choice == 2:  # SQLITE3
            logger.debug("SQLITE chosen")
            userdata.update(
                {
                    "DATABASE": {
                        "type": "sqlite",
                        "connection":
                            {
                                "database": "series"
                            }
                    }
                })
            # TODO: test sqlite
        logger.debug("Config finished")
        logger.debug("Writing version file")
        with open(version_file_path, "w") as f:
            json.dump(userdata, f)
        logger.debug("Writing done")

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
    :return: UPDATE_* definition based on the available update
    """

    logger = logging.getLogger("Program.{}".format("check_update"))
    try:
        # Get local installed version
        with open("version.json") as f:
            version = json.load(f)
        local_version = version["version"]
        logger.debug("Local version found: %s" % local_version)
        # Get remote version

        from github import Github

        github = Github(GITHUB_TOKEN)
        repo = github.get_repo("alexregazzo/%s" % REPO_NAME)
        remote_version_data = None
        try:
            content_file = repo.get_contents("version.json", BRANCH_NAME)
            response = requests.get(content_file.download_url)
            if response.status_code == 200:
                remote_version_data = json.loads(response.text)
        except:
            logger.exception("Unexpected exception ocurred while trying to get version file from github")
            return UPDATE_NONE

        if remote_version_data is None:
            logger.critical("Could not get version file")
            return UPDATE_NONE
        remote_version = remote_version_data['version']
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
                    return UPDATE_MAJOR
                elif k == 1:  # minor
                    logger.debug("Minor update")
                    return UPDATE_MINOR
                elif k == 2:  # patch/bugfix
                    logger.debug("Patch/bugfix update")
                    return UPDATE_PATCH_OR_BUG_FIX
                else:
                    raise NotImplementedError("Something went wrong on versions comparisons comparison - local: %s, remote: %s" % (local_version, remote_version))
        logger.debug("No update")
        return UPDATE_NONE
    except:
        logger.exception("An exception ocurred while trying to execute check updates")
        return UPDATE_NONE


def update():
    logger = logging.getLogger("Program.{}".format("update"))
    logger.debug("Updating")
    try:
        # get current version
        with open("version.json") as f:
            userdata = json.load(f)

        # delete keys expect user config
        for key in [key for key in userdata if key not in ["TMDB", "DATABASE"]]:
            del userdata[key]

        # confirm delete of existing files
        from send2trash import send2trash
        if input("All files on this folder will be deleted, would you like to continue?[y/n]").lower() != "y":
            logger.debug("Quitting by user")
            print("Quitting...")
            os.system("pause")
            sys.exit(0)

        # connect to github
        logger.debug("Importing github")
        from github import Github
        print("Connecting...")
        logger.debug("Connect to github")
        github = Github(GITHUB_TOKEN)
        repo = github.get_repo("alexregazzo/%s" % REPO_NAME)

        # download files
        logger.debug("Download starting")
        print("Downloading...")
        all_files = []
        contents = repo.get_contents("", BRANCH_NAME)
        version_file_found = False
        number_of_errors = 0
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
                            logger.debug("Found version file")
                            logger.debug("Updating current version file")
                            userdata.update(json.loads(response.text))
                            all_files.append({
                                "path": path,
                                "content": json.dumps(userdata)
                            })
                            version_file_found = True
                        else:
                            all_files.append({
                                "path": path,
                                "content": response.text
                            })
                        logger.debug("Success download on %s" % path)
                        break
                    else:
                        print("Error, retrying")
                        logger.warning("Request error on file %s" % path)
                else:
                    print("Failed on file %s" % content_file.path)
                    logger.critical("Problem while downloading %s" % path)
                    number_of_errors += 1
        logger.debug("Problems found: %d" % number_of_errors)
        logger.debug("Downloading files done")
        print("Downloading files done")
        print("Errors found: %d" % number_of_errors)
        if version_file_found is False:
            logger.critical("Version file was not found!")
        if number_of_errors > 0 or version_file_found is False:
            print("There were errors while downloading the files so the update will not continue")
            print("Check your internet connection and try again later")
            print("If the error persists, contact the developer")
            os.system("pause")
            sys.exit(1)

        # delete files
        logger.debug("Delete files")
        print("Deleting files")
        for current_dir, folder, files in os.walk("."):
            if current_dir in [".\logs", ".\idea"]:
                logger.debug("Continuing on %s" % current_dir)
                continue
            for file in files:
                logger.debug("Deleting %s" % os.path.join(current_dir, file))
                print("Deleting %s" % os.path.join(current_dir, file))
                try:
                    send2trash(os.path.join(current_dir, file))
                except PermissionError:
                    logger.warning("Permission error on file %s" % os.path.join(current_dir, file))
                else:
                    logger.debug("Deleted")
        logger.debug("File deletion finished")
        print("Deleting files done")

        logger.debug("Write files on disk")
        print("Writting files on disk")
        for file in all_files:
            logger.debug("Writting %s" % file['path'])
            print("Writting %s" % file['path'])
            with open(file['path'], 'w') as f:
                f.write(file['content'])
            logger.debug("Success")
        logger.debug("Writting done")
        print("Writting done")

        # install modules
        logger.debug("Installing modules")
        print("Installing modules")
        os.system("pip install -r requirements.txt")
        print("Finish installing modules")
        logger.debug("Finished installing modules")

        logger.debug("Finished updating")
        print("Updating finished successfully")
        print("Reopen Downloader to continue")
        os.system("pause")
        return
    except:
        logger.exception("An unexpeced error ocurred while trying to update")


if __name__ == "__main__":
    pass
    # install()
