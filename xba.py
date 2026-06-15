import json
import os

import requests

from characters import mappings, POSITIONS

GRID_BUCKET_SIZE = 5
HEIGHT_BUCKET_SIZE = 10

url = "https://api.projectrio.app/landing_data/?limit_games=1500&tag=StarsOffSeason6&tag=StarsOffSeason5&stadium=0&stadium=1&stadium=2&stadium=3&stadium=5"
file = "event_data.txt"

hit_outcomes = [7, 8, 9, 10]
hit_weights = {
    7: 0.403,
    8: 0.781,
    9: 1.058,
    10: 1.581
}
out_value = 0.393
out_outcomes = [1, 4, 5, 6, 14, 15, 16]

event_dict = {}
position_total = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}

fielders = {}
fielder_game_ids = {}
fielder_positions = { None: []}
for i in range(54):
    fielder_positions[i] = []

if os.path.exists("event_data.txt"):
    with open("event_data.txt") as file:
        response = file.read()
else:
    response = requests.get(url).text
    with open("event_data.txt", "w") as file:
        file.write(response)

# print(response)
events = sorted(json.loads(response).get("Data", {}), key=lambda x: (x["game_id"], x["event_num"]))


def mround(num, multiple):
    return multiple * round(num / multiple)


for event in events:
    # east/west pos on the field
    x_pos = event["ball_x_landing_pos"]
    # vertical pos
    y_pos = event["ball_y_landing_pos"]
    # north/south pos on the field
    z_pos = event["ball_z_landing_pos"]

    max_height = event["ball_hang_time"]

    bucket = (mround(x_pos, GRID_BUCKET_SIZE), mround(z_pos, GRID_BUCKET_SIZE), mround(max_height, HEIGHT_BUCKET_SIZE))

    if bucket in event_dict:
        event_dict[bucket].append(event)
    else:
        event_dict[bucket] = [event]

sorted_list = sorted(event_dict, key=lambda x: len(event_dict[x]), reverse=True)

for bucket in sorted_list:
    hit_count = 0
    hit_value = 0
    out_count = 0
    for event in event_dict[bucket]:
        outcome = event["final_result"]
        if outcome in hit_outcomes:
            hit_count += 1
            hit_value += hit_weights[outcome] + out_value
        elif outcome in out_outcomes:
            out_count += 1
    ball_count = hit_count + out_count
    if ball_count > 0:
        xba = hit_count / ball_count
        woba = hit_value / ball_count
        for event in event_dict[bucket]:
            outcome = event["final_result"]
            if outcome in out_outcomes:
                if event["fielder_position"] is not None and event["fielder_char_id"] is not None:
                    position_total[event["fielder_position"]] += woba

                    if event["fielder_char_id"] in fielders:
                        fielders[event["fielder_char_id"]].append(woba)
                    else:
                        fielders[event["fielder_char_id"]] = [woba]

            # if event["batter_char_id"] in fielder_game_ids:
            #     if event["game_id"] not in fielder_game_ids[event["batter_char_id"]]:
            #         fielder_game_ids[event["batter_char_id"]].append(event["game_id"])
            # else:
            #     fielder_game_ids[event["batter_char_id"]] = [event["game_id"]]

            if event["fielder_char_id"] in fielder_game_ids:
                if event["game_id"] not in fielder_game_ids[event["fielder_char_id"]]:
                    fielder_game_ids[event["fielder_char_id"]].append(event["game_id"])
                    fielder_positions[event["fielder_char_id"]].append(event["fielder_position"])
            else:
                fielder_game_ids[event["fielder_char_id"]] = [event["game_id"]]
                fielder_positions[event["fielder_char_id"]].append(event["fielder_position"])

        # print(str(bucket) + ": " + str(len(event_dict[bucket])) + " events")
        # print("xBA:", "{:.3f}".format(xba), "wOBA:", "{:.3f}".format(woba), "on", ball_count, "balls in play")
        # print()

sorted_fielders = sorted(fielders, key=lambda x: sum(fielders[x]), reverse=True)

for fielder in sorted_fielders:
    avg_runs = 0
    total_games = len(fielder_game_ids.get(fielder, 0))
    total_runs = sum(fielders[fielder])
    if fielder in fielder_positions:
        for i in range(9):
            count = fielder_positions[fielder].count(i)
            # if count > 0:
            #     print(count, "games at", POSITIONS[i])
            avg_runs += (count * (position_total[i] / 3000))
    print(mappings[fielder], "(" + str(total_games) + " games):", "{:.2f}".format(total_runs / total_games), "runs saved per game,",
          "{:.2f}".format((total_runs - avg_runs) / total_games), "RAA")

for position in position_total:
    print(POSITIONS[position], "{:.3f}".format(position_total[position] / 3000))
