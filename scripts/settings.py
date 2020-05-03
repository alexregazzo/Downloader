import os
import json

LOG_FORMAT = "%(asctime)s - %(levelname)s :: (%(threadName)-9s) :: %(name)s  %(lineno)d :: %(message)s"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENT_DIR = os.path.dirname(__file__)
DEVELOMENT_MODE = ".testing" in os.listdir(os.path.join(CURRENT_DIR, "./.."))
with open(os.path.join(CURRENT_DIR, "config/relative-paths.json")) as f:
    RELATIVE_PATHS = json.load(f)

ABSOLUTE_PATHS = {key: os.path.join(CURRENT_DIR, value) for key, value in RELATIVE_PATHS.items()}
for path in ABSOLUTE_PATHS.values():
    os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    print(ABSOLUTE_PATHS)
