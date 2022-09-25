import requests
from utils import char_name_dict as char_name_dict

url = "https://projectrio-api-1.api.projectrio.app/landing_data/?limit_games=100"

hit_outcomes = [7, 8, 9, 10]
out_outcomes = [1, 4, 5, 6, 14, 15, 16]

event_dict = {}

events = requests.get(url).json()


def mround(num, multiple):
    return multiple * round(num / multiple)


for event in events["Data"]:
    # east/west pos on the field
    x_pos = event["ball_x_pos"]
    # vertical pos
    y_pos = event["ball_y_pos"]
    # north/south pos on the field
    z_pos = event["ball_z_pos"]

    max_height = event["ball_max_height"]

    bucket = (mround(x_pos, 5), mround(z_pos, 5), mround(max_height, 5))

    if bucket in event_dict:
        event_dict[bucket].append(event)
    else:
        event_dict[bucket] = [event]

for bucket in event_dict:
    hit_count = 0
    out_count = 0
    for event in event_dict[bucket]:
        outcome = event["final_result"]
        if outcome in hit_outcomes:
            hit_count += 1
        elif outcome in out_outcomes:
            out_count += 1
    ball_count = hit_count + out_count
    if ball_count > 1:
        xba = hit_count / ball_count
        print(str(bucket) + ": " + str(len(event_dict[bucket])) + " events")
        print("xBA:", "{:.3f}".format(xba), "on", ball_count, "balls in play")
        print()

