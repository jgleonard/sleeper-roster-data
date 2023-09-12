#!/usr/bin/env python3

"""Modules providing argument parsing, json support and html api support"""
import argparse
import json
import logging
import os
import requests
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
channel_id = os.environ.get("SLACK_CHANNEL")
logger = logging.getLogger(__name__)

def get_week():
  """Gets the current NFL week

  Args:
    None

  Returns:
    Integer of current NFL week
  """
  url = "https://api.sleeper.app/v1/state/nfl"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching NFL state: {response.status_code}")

  return json.loads(response.content)['week']


def get_matchups(league_id,week):
  """Gets the matchups for a Sleeper fantasy football league.

  Args:
    league_id: The ID of the league.
    week: Current week.

  Returns:
    A dictionary of scores
  """

  result = {}

  url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching matchups: {response.status_code}")

  scores = json.loads(response.content)

  for roster in scores:
    result[roster['roster_id']] = { "matchup": roster['matchup_id'], "points": roster['points'] }

  return result

def get_rosters(league_id):
  """Gets the rosters for a Sleeper fantasy football league.

  Args:
    league_id: The ID of the league.

  Returns:
    A dictionary of usernames using the roster_id as keys.
  """

  roster_map = {}
  user_map = {}

  url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching rosters: {response.status_code}")

  rosters = json.loads(response.content)

  for roster in rosters:
    roster_map[roster['roster_id']] = roster['owner_id']

  url = f"https://api.sleeper.app/v1/league/{league_id}/users"

  response = requests.get(url,timeout=10)
  if response.status_code != 200:
    raise Exception(f"Error fetching users: {response.status_code}")

  users = json.loads(response.content)

  for user in users:
    user_map[user['user_id']] = user['display_name']

  result = list(map(lambda x: user_map[roster_map[x]], roster_map))

  return result


def main():
  """
  Main function
  """
  parser = argparse.ArgumentParser(description="Print scores for Sleeper league",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("league-id", type=int, help="Sleeper league ID")
  args = parser.parse_args()
  config = vars(args)

  league_id = config["league-id"]

  rosters = get_rosters(league_id)

  if rosters is None:
    print(f"No roster data found for league {league_id}")
    return

  week = get_week()-1
  scores = get_matchups(league_id,week)

  if scores is None:
    print(f"No score data found for league {league_id}")
    return

  matches = {}

  for match_id,match_info in scores.items():
    if match_info['matchup'] in matches.keys():
      matches[match_info['matchup']].update({rosters[int(match_id-1)]: match_info['points']})
    else:
      matches.update({match_info['matchup']: {rosters[int(match_id-1)]: match_info['points']}})

  text_output = f"Week {week} Scores\n\n"
  block_output = [{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": f"Week {week} Scores",
			}
		},{
			"type": "divider",
		}]

  for match_id,match in sorted(matches.items()):
    # text_output += f"Matchup {match_id}:\n"
    elements = []
    for team,points in match.items():
      elements.append({ "type": "mrkdwn", "text": f"*{team}*: {points}" })

    elements.insert(1,{ "type": "mrkdwn", "text": "VS" })

    # block_output.append({ "type": "section", "fields": elements })
    block_output.append({ "type": "context", "elements": elements })

  try:
    # Call the conversations.list method using the WebClient
    result = client.chat_postMessage(
        channel=channel_id,
        text=text_output,
        # You could also use a blocks[] array to send richer content
        blocks=block_output
    )
    # Print result, which includes information about the message (like TS)
    print(result)

  except SlackApiError as e:
    print(f"Error: {e}")



if __name__ == "__main__":
  main()
