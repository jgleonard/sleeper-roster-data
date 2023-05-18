#!/usr/bin/env python3

"""Modules providing argument parsing, json support and html api support"""
import argparse
import json
import requests


def get_bye_weeks():
  """Gets the bye weeks using the ESPN API

  Args:
    None

  Returns:
    Dict of bye weeks.
  """

  # Fetch current league year
  url = "https://api.sleeper.app/v1/state/nfl"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching season info: {response.status_code}")

  year = int(json.loads(response.content)['season'])

  bye_weeks = {}

  # Fetch bye weeks from ESPN
  for i in range(1, 37):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{i}/schedule?season={year}"

    response = requests.get(url,timeout=10)
    if response.status_code != 200:
      raise Exception(f"Error fetching team {i} bye week: {response.status_code}")

    response_data = json.loads(response.content)

    # Filter out non-teams from ESPN data
    if not "byeWeek" in response_data:
      continue

    # ESPN uses a different abbreviation for Washington than Sleeper
    if response_data['team']['abbreviation'] == "WSH":
      bye_weeks['WAS'] =  int(response_data['byeWeek'])
    else:
      bye_weeks[response_data['team']['abbreviation']] =  int(response_data['byeWeek'])

  return bye_weeks

def get_user_id(username):
  """Gets the userid for a Sleeper fantasy football username

  Args:
    username: The username of the user.

  Returns:
    Userid.
  """

  url = f"http://api.sleeper.app/v1/user/{username}"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching user: {response.status_code}")

  return int(json.loads(response.content)['user_id'])

def get_rosters(league_id):
  """Gets the rosters for a Sleeper fantasy football league.

  Args:
    league_id: The ID of the league.

  Returns:
    A list of rosters.
  """

  url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching rosters: {response.status_code}")

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

  with open("player_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

  player_data = {}
  for key, value in data.items():
    player_data[key] = value

  bye_weeks = get_bye_weeks()

  roster_data = {}

  # Iterate over positions and players to build roster and add bye info
  for playerid in players:
    player = player_data[playerid]
    roster_data[playerid] = player
    roster_data[playerid]["bye"] = bye_weeks[player["team"]]

  # Sort roster by position and bye week
  return sorted(roster_data.items(), key=lambda x: (x[1]["position"], x[1]["bye"]))


def main():
  """
  Main function
  """
  parser = argparse.ArgumentParser(description="Print byes for Sleeper team or dump roster data",
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
    print(f"No roster found for userid {userid}")
    return

  sorted_roster = sort_roster(roster)

  # If JSON requested, print that out, otherwise, default output
  if config["json"]:
    print(json.dumps(sorted_roster))
  else:
    # Print out the sorted players, position and bye week
    for player in sorted_roster:
      print(f"{player[1]['full_name']} | {player[1]['position']} | {player[1]['bye']}")

if __name__ == "__main__":
  main()
