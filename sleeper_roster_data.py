#!/usr/bin/env python3

import requests
import json
import argparse

# Hardcoded for 2023
bye_weeks = {
  "ARI": 14,
  "ATL": 11,
  "BAL": 13,
  "BUF": 13,
  "CAR": 7,
  "CHI": 13,
  "CIN": 7,
  "CLE": 5,
  "DAL": 7,
  "DEN": 9,
  "DET": 9,
  "GB": 6,
  "HOU": 7,
  "IND": 11,
  "JAX": 9,
  "KC": 10,
  "LV":  13,
  "LAC": 5,
  "LAR": 10,
  "MIA": 10,
  "MIN": 13,
  "NE": 11,
  "NO": 11,
  "NYG": 13,
  "NYJ": 7,
  "PHI": 10,
  "PIT": 6,
  "SF": 9,
  "SEA": 5,
  "TB": 5,
  "TEN": 7,
  "WAS": 14,
}

def get_user_id(username):
  """Gets the userid for a Sleeper fantasy football username

  Args:
    username: The username of the user.

  Returns:
    Userid.
  """

  url = "http://api.sleeper.app/v1/user/{}".format(username)

  response = requests.get(url)
  if response.status_code != 200:
    raise Exception("Error fetching user: {}".format(response.status_code))

  return int(json.loads(response.content)['user_id'])

def get_rosters(league_id):
  """Gets the rosters for a Sleeper fantasy football league.

  Args:
    league_id: The ID of the league.

  Returns:
    A list of rosters.
  """

  url = "https://api.sleeper.app/v1/league/{}/rosters".format(league_id)

  response = requests.get(url)
  if response.status_code != 200:
    raise Exception("Error fetching rosters: {}".format(response.status_code))

  return json.loads(response.content)

def get_roster_by_user(rosters, userid):
  """Gets the roster that matches the userid.

  Args:
    rosters: A list of rosters.
    userid: The userid of the roster to get.

  Returns:
    The roster that matches the userid.
  """

  for roster in rosters:
    if int(roster["owner_id"]) == userid:
      return roster
  return None

def sort_roster(roster):
  """Sorts the players of a roster by position and bye week.

  Args:
    roster: The roster to print.
  """

  players = roster["players"]

  # Pull source data in from Sleeper data file
  # origin: GET https://api.sleeper.app/v1/players/nfl

  with open("player_data.json", "r") as f:
    data = json.load(f)

  player_data = {}
  for key, value in data.items():
    player_data[key] = value

  roster_data = {}

  # Iterate over positions and players to build roster and add bye info
  for playerid in players:
    player = player_data[playerid]
    roster_data[playerid] = player
    roster_data[playerid]["bye"] = bye_weeks[player["team"]] 

  # Sort roster by position and bye week
  return sorted(roster_data.items(), key=lambda x: (x[1]["position"], x[1]["bye"]))


def main():
  parser = argparse.ArgumentParser(description="Print out bye weeks for Sleeper team or dump roster data", 
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("league-id", type=int, help="Sleeper league ID")
  parser.add_argument("username", help="Sleeper username")
  parser.add_argument("-j", "--json", action="store_true", help="Output full roster data in JSON")
  args = parser.parse_args()
  config = vars(args)
  
  league_id = config["league-id"]
  username = config["username"]
  userid = get_user_id(username)

  rosters = get_rosters(league_id)
  roster = get_roster_by_user(rosters, userid)

  if roster is None:
    print("No roster found for userid {}".format(userid))
    return

  sorted_roster = sort_roster(roster)

  # If JSON requested, print that out, otherwise, default output
  if config["json"]:
    print(json.dumps(sorted_roster))
  else:
    # Print out the sorted players, position and bye week
    for id, player in sorted_roster:
      print("{} | {} | {}".format(player["full_name"], player["position"], player["bye"]))

if __name__ == "__main__":
  main()
