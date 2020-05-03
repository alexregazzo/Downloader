# Serie Downloader 
Python program which objective is to easily (automatically)
download series' episodes to be watched.

## How to use
- **Clone** the git repository
- [Download](https://raw.githubusercontent.com/alexregazzo/Downloader/organize/setup.py) and run **setup**
> Note: by clicking the 'download' button you will be redirected to the github page that contains that file, save it by pressing ctrl + s
- Run **main** whenever you want the program to run

#### Requirements:
* [Python](https://www.python.org/downloads/) version >= 3.8
* Connection to the internet
* Some python packages listed on [requirements.txt](./requirements.txt)
* API key from [TMDB](https://www.themoviedb.org/settings/api)
* [uTorrent](https://www.utorrent.com/intl/pt/downloads/win_us) (current version (v2.0) might work on other torrent clients (might change on later updates))

### v3.0 new features
- No longer support mysqlserver (all on sqlite3) so database setup is required
- Setup which allows installation and updates

### v2.0 new features
- User features:
>- Setup: file that makes startup easy
>- List recently added episodes (only episodes within 3 hours)
>- List last added episodes (the last 10 added)
>- List episodes that has no link and are supposed to be downloaded
- Changes:
>- Database: links separated from episode allowing more than one link per episode
>- Database: all the selects are now returning dicts instead of tuples allowing easier changes in the future
>- Multiple log files according to its level to easy debbugging
>- Updating release/development type of recognition
>- Better documenting files
>- Removing passwords from github and make it user settable and make it github public (so it won't have previous changes to code)
>- Change the way links are found
>- Adding requirements file containing packages that should be installed (installed on setup)
>- Changing how the tables are created


### v1.0 features
- User features:
>- Download episode from a specific episode until the end
>- Download a single episode
>- List added series
>- List to download episodes
>- Add serie
>- Remove serie
- Auto update series episodes
- Auto update and download newly added episodes
- Auto search torrent link in thepiratebay
- Multiple tasks running in differents threads
- Connection with TMDB
- Cache link search
- Cache TMDB search
- Requirements:
>- uTorrent installed
>- Microsoft Server running when the program is ran

