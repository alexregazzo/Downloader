# Serie Downloader 
Python program which objective is to easily (automatically)
download series' episodes to be watched.

## How to use
- **Clone** the git repository
- Run **setup**
- Run **main** whenever you want the program to run 

#### Requirements:
* Connection to the internet
* Some python packages listed on [requirements.txt](./requirements.txt)
* [Mysql server](https://dev.mysql.com/downloads/mysql/) installed locally (can run remotely if configured)
* API key from [TMDB](https://www.themoviedb.org/settings/api)
* [uTorrent](https://www.utorrent.com/intl/pt/downloads/win_us) (current version (v2.0) might work on other torrent clients (might change on later updates)) 

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

