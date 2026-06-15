import requests

url = "https://api.projectrio.app/games/?tag=StarsOffSeason6&tag=StarsOffSeason7&limit_games=5000"
games_response = requests.get(url).json()

user_dict = {"all": []}

for game in games_response["games"]:
    if game["away_user"] not in user_dict:
        user_dict[game["away_user"]] = []
    if game["home_user"] not in user_dict:
        user_dict[game["home_user"]] = []
    if game["away_score"] > game["home_score"]:
        user_dict[game["away_user"]].append(game["loser_incoming_elo"])
        user_dict[game["home_user"]].append(game["winner_incoming_elo"])
    elif game["home_score"] > game["away_score"]:
        user_dict[game["home_user"]].append(game["loser_incoming_elo"])
        user_dict[game["away_user"]].append(game["winner_incoming_elo"])
    user_dict["all"].append(game["loser_incoming_elo"])
    user_dict["all"].append(game["winner_incoming_elo"])

user_tuples = []

for user in user_dict:
    if len(user_dict[user]) > 10:
        user_tuples.append((user, round(sum(user_dict[user]) / len(user_dict[user]))))

user_tuples.sort(key=lambda x: x[1], reverse=True)

for u in user_tuples:
    print(u)
