import requests

print("Enter position (blank for all stats):")
pos = input().lower()
print("Enter '0' for stars-off data; '1' for stars-on")
stars = int(input())
print("Enter '0' for all data, '1' for ranked only")
ranked = int(input())

url = "https://projectrio-api-1.api.projectrio.app/detailed_stats/?exclude_batting=1&exclude_misc=1"

if stars == 0:
    url += "&tag=Normal"
elif stars == 1:
    url += "&tag=Superstar"
if ranked == 1:
    url += "&tag=Ranked"

positions = ["p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf"]
averages = {}

total_json = requests.get(url).json()

pitches_per_game = total_json["Stats"]["Pitching"]["total_pitches"] / (total_json["Stats"]["Pitching"]["outs_pitched"] / 27)

for position in positions:
    games = total_json["Stats"]["Fielding"]["pitches_per_" + position] / pitches_per_game
    outs_per_game = total_json["Stats"]["Fielding"]["outs_per_" + position] / games
    averages[position] = outs_per_game
    print(position.upper(), round(outs_per_game, 2), "outs per 9 innings in", round(games), "games")

response_json = requests.get("https://projectrio-api-1.api.projectrio.app/detailed_stats/?by_char=1&tag=Normal&tag=Ranked&exclude_batting=1&exclude_pitching=1&exclude_misc=1").json()

for character in response_json["Stats"]:
    stats = response_json["Stats"][character]["Fielding"]
    for position in positions:
        if stats["outs_per_" + position] > 50 and (position == pos or pos == ""):
            games = stats["pitches_per_" + position] / pitches_per_game
            outs_per_game = stats["outs_per_" + position] / games
            print(character, position.upper(), round(outs_per_game - averages[position], 2), "outs above average per 9 innings in", round(games, 1), "games")
