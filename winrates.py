from json import JSONDecodeError

import glicko2
import requests

from characters import mappings

timestamp = 1716177600

result_dict = {}
for i in range(54):
    result_dict[i] = {
        "Games": 0,
        "Wins": 0,
        "Losses": 0,
        "Elo": [],
        "Opponent Elo": []
    }

while True:
    base_url = f"https://api.projectrio.app/games/?limit_games=100&include_teams=1&tag=S9SuperstarsOff&start_time={timestamp}&end_time={timestamp + 86400}"
    games_response = requests.get(base_url)
    try:
        games_data = games_response.json()
    except JSONDecodeError:
        print("error")
        continue
    if len(games_data["games"]) == 0:
        break

    print(len(games_data["games"]))

    for game in games_data["games"]:
        # FILTERS - No garden and both players 1500+
        if game["stadium"] != 4 and game["winner_incoming_elo"] > 1500 and game["loser_incoming_elo"] > 1500:
            (winner_roster, loser_roster) = (game["home_roster"], game["away_roster"]) if game["home_score"] > game["away_score"] else (game["away_roster"], game["home_roster"])

            for char in winner_roster.values():
                result_dict[char]["Games"] += 1
                result_dict[char]["Wins"] += 1
                result_dict[char]["Elo"].append(game["winner_incoming_elo"])
                result_dict[char]["Opponent Elo"].append(game["loser_incoming_elo"])

            for char in loser_roster.values():
                result_dict[char]["Games"] += 1
                result_dict[char]["Losses"] += 1
                result_dict[char]["Elo"].append(game["loser_incoming_elo"])
                result_dict[char]["Opponent Elo"].append(game["winner_incoming_elo"])

    timestamp = timestamp + 86400

for char_id, value in result_dict.items():
    if value["Games"] > 0:
        avg_elo = sum(value["Elo"]) / len(value["Elo"])
        opp_elo = sum(value["Opponent Elo"]) / len(value["Opponent Elo"])
        elo_diff = avg_elo - opp_elo
        p1 = glicko2.Player(avg_elo, 150)
        p2 = glicko2.Player(opp_elo, 150)
        p1.update_player([opp_elo], [150], [1])
        p2.update_player([avg_elo], [150], [1])
        num1 = p1.rating - avg_elo
        num2 = p2.rating - opp_elo
        expected_win = num2 / num1
        value["expected_win_pct"] = expected_win / (expected_win + 1) * 100

sorted_list = sorted(result_dict, key=lambda x: (result_dict[x]["Wins"] / result_dict[x]["Games"]) * 100 - result_dict[x]["expected_win_pct"] if result_dict[x]["Games"] > 0 else 0, reverse=True)

for char_id in sorted_list:
    if result_dict[char_id]["Games"] > 10:
        elo_diff = (sum(result_dict[char_id]["Elo"]) / len(result_dict[char_id]["Elo"])) - (sum(result_dict[char_id]["Opponent Elo"]) / len(result_dict[char_id]["Opponent Elo"]))
        print(f'{mappings[char_id]}: {result_dict[char_id]["Wins"]}-{result_dict[char_id]["Losses"]} ({(result_dict[char_id]["Wins"] / result_dict[char_id]["Games"] * 100):.2f}%), Average elo diff {round(elo_diff)}, expected {result_dict[char_id]["expected_win_pct"]:.2f}%')
