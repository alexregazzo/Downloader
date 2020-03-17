import os
import json

DEVELOMENT_MODE = ".testing" in os.listdir(".")
with open("userconfig/database.json") as f:
    database_data = json.load(f)

DATABASE = database_data["database"]["development"] if DEVELOMENT_MODE else database_data["database"]["release"]
FILEMANAGER = {"ROOT_DIR": "", "DEST_DIR": ""}
