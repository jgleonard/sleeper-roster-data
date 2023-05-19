# sleeper-roster-data
Python Tool for pulling roster data from Sleeper and displaying bye weeks by position.

# Flat
Player data fetched weekly from Sleeper and available for use in the [Flat Viewer](https://flatgithub.com/jgleonard/sleeper-roster-data?filename=player_data.json).

# Usage
```
√ sleeper-roster-data  % python3 ./sleeper_roster_data.py -h
usage: sleeper_roster_data.py [-h] [-j] league-id username

Print out bye weeks for Sleeper team or dump roster data

positional arguments:
  league-id   Sleeper league ID
  username    Sleeper username

options:
  -h, --help  show this help message and exit
  -j, --json  Output full roster data in JSON (default: False)
```

# Sample
![Screenshot 2023-05-18 at 2 19 39 PM](https://github.com/jgleonard/sleeper-roster-data/assets/26628621/c5d41236-6146-4557-a0e2-35cd5afb723c)

# Requirements
Python3 and the script assumes that player data has been downloaded from Sleeper's API already and stored as player_data.json
```
curl -so player_data.json https://api.sleeper.app/v1/players/nfl
```

# Python Dependencies
* requests
* argpase

```
pip install -r requirements.txt
```
