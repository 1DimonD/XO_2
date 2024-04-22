import json
import os
from datetime import datetime

import requests
import pandas as pd

from config import FOOTBALL_API_HEADERS, LEAGUE_DICT_PATH, TEAM_DICT_PATH
from image_makers import create_players_table, create_result_table, create_wind_rose_by_predictions
from string_transformers import create_current_matches_string


def get_league_dict():
    if os.path.exists(LEAGUE_DICT_PATH):
        f = open(LEAGUE_DICT_PATH, 'r')
        tmp = ''.join(f.readlines())
        f.close()
        return json.loads(tmp)

    # Endpoint for retrieving all available leagues
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Create a dictionary to store league names and IDs
            league_dict = {}

            # Iterate through each league in the response
            for league in data['response']:
                # Extract league name and ID
                league_name = league['league']['name']
                league_id = league['league']['id']

                # Add league name and ID to the dictionary
                league_dict[league_name] = league_id

            f = open(LEAGUE_DICT_PATH, 'w')
            f.write(json.dumps(league_dict))
            f.close()
            return league_dict

        else:
            print("Failed to retrieve league data. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


LEAGUES_DICT = get_league_dict()


def get_teams_dict(league_name):

    url = 'https://api-football-v1.p.rapidapi.com/v3/teams'

    params = {
        'league': LEAGUES_DICT[league_name],
        'season': datetime.now().year-1
    }

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Create a dictionary to store team names and IDs
            teams_dict = {}

            # Iterate through each team in the response
            for team in data['response']:
                # Extract team name and ID
                team_name = team['team']['name']
                team_id = team['team']['id']

                # Add team name and ID to the dictionary
                teams_dict[team_name] = team_id

            return teams_dict

        else:
            print("Failed to retrieve teams data. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


TEAMS_DICT = {}


def update_team_dict(league_name):
    global TEAMS_DICT
    TEAMS_DICT = get_teams_dict(league_name)


def get_team_dict():
    return TEAMS_DICT


def get_league_table(league_name):

    league_id = LEAGUES_DICT[league_name]

    endpoint = f"https://api-football-v1.p.rapidapi.com/v3/standings"
    params = {
        "season": datetime.now().year-1,
        "league": league_id
    }

    try:
        response = requests.get(endpoint, headers=FOOTBALL_API_HEADERS, params=params)
        data = response.json()

        f = open('tmp.txt', 'w')
        f.write(json.dumps(data))
        f.close()

        # Check if the request was successful
        if response.status_code == 200:
            if data['response']:
                standings = data['response'][0]['league']['standings'][0]

                # Prepare data for the DataFrame
                table_data = []
                for team in standings:
                    position = team['rank']
                    team_name = team['team']['name']
                    matches = team['all']['played']
                    won = team['all']['win']
                    draw = team['all']['draw']
                    lost = team['all']['lose']
                    points = team['points']
                    table_data.append(
                        {"Position": position, "Team": team_name, "Matches": matches, "Won": won, "Draw": draw,
                         "Lost": lost, "Points": points})

                # Create DataFrame
                df = pd.DataFrame(table_data)
                return df
            else:
                print("No standings found for the given league.")
                return None
        else:
            print(f"Error: {data['errors'][0]['message']}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def determine_result(scoreline):
    home_goals, away_goals = map(int, scoreline.split(":"))
    if home_goals > away_goals:
        return "W"
    elif home_goals == away_goals:
        return "D"
    else:
        return "L"


def get_team_form(team_name):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    params = {
        "team": TEAMS_DICT[team_name],
        "last": 10
    }

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Extract recent results
            fixtures = data['response']
            form_data = []
            for fixture in fixtures:
                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                home_goals = fixture['goals']['home']
                away_goals = fixture['goals']['away']

                result = ""
                opponent_team = ""

                if team_name == home_team:
                    opponent_team = away_team
                    result = f"{home_goals}:{away_goals}"
                elif team_name == away_team:
                    opponent_team = home_team
                    result = f"{away_goals}:{home_goals}"

                form_data.append({"result": result, "opponent_team": opponent_team})

            # Create DataFrame from form_data
            df = pd.DataFrame(form_data)

            # Add "W/D/L" column
            df['W/D/L'] = df['result'].apply(lambda x: determine_result(x))

            return df

        else:
            print("Failed to retrieve team form. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


def get_team_players(team_name):
    url = 'https://api-football-v1.p.rapidapi.com/v3/players/squads'

    params = {
        "team": TEAMS_DICT[team_name]
    }

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Extract player information
            players_data = data['response'][0]['players']
            players_info = []
            for player in players_data:
                player_info = {
                    "number": player.get('number', ''),
                    "position": player.get('position', ''),
                    "name": player.get('name', ''),
                    "age": player.get('age', '')
                }
                players_info.append(player_info)

            # Create DataFrame from players_info
            df = pd.DataFrame(players_info)

            return df

        else:
            print("Failed to retrieve team players. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


def get_current_matches_by_league(league_name):
    url = 'https://api-football-v1.p.rapidapi.com/v3/fixtures'

    params = {
        "live": f'{LEAGUES_DICT[league_name]}-{LEAGUES_DICT[league_name]}'
    }

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Extract current matches data
            matches_data = data['response']
            matches_info = []
            for match in matches_data:
                match_id = match['fixture']['id']
                teams = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                current_result = match['goals']['home'] if match['goals']['home'] is not None else 0, match['goals'][
                    'away'] if match['goals']['away'] is not None else 0
                half = match['fixture']['status']['short']
                time = match['fixture']['status']['elapsed']

                matches_info.append({
                    "id": match_id,
                    "teams": teams,
                    "current_result": f"{current_result[0]}:{current_result[1]}",
                    "half": half,
                    "time (in minutes)": time
                })

            # Create DataFrame from matches_info
            df = pd.DataFrame(matches_info)

            return df

        else:
            print("Failed to retrieve current matches. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


def get_prediction_by_fixture_id(fixture_id):
    url = 'https://api-football-v1.p.rapidapi.com/v3/predictions'

    params = {
        "fixture": fixture_id
    }

    try:
        # Make GET request to the API endpoint
        response = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()

            # Extract predictions data
            predictions_data = data['response'][0]

            # Extract teams
            home_team = predictions_data['teams']['home']['name']
            away_team = predictions_data['teams']['away']['name']

            # Extract comparison fields
            comparison_fields = list(predictions_data['comparison'].keys())
            comparison_fields.remove('poisson_distribution')
            # Extract predictions, remove percent sign, and convert to decimal format
            home_predictions = []
            away_predictions = []
            for field in comparison_fields:
                home_pred_str = predictions_data['comparison'][field]['home']  # Get prediction as string
                away_pred_str = predictions_data['comparison'][field]['away']  # Get prediction as string
                home_pred = float(home_pred_str.rstrip('%')) / 100  # Remove percent sign and convert to decimal
                away_pred = float(away_pred_str.rstrip('%')) / 100  # Remove percent sign and convert to decimal
                home_predictions.append(home_pred)
                away_predictions.append(away_pred)

            # Create DataFrame
            df = pd.DataFrame({
                home_team: home_predictions,
                away_team: away_predictions
            }, index=comparison_fields)

            return df

        else:
            print("Failed to retrieve predictions. Status code:", response.status_code)
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None
