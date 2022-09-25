import requests

linear_weights = {
    0: 0,       # None
    1: -0.407,
    2: 0.336,   # Walk
    3: 0.336,   # Walk
    4: -0.407,
    5: -0.407,
    6: -0.407,
    7: 0.406,   # Single
    8: 0.778,   # Double
    9: 1.094,   # Triple
    10: 1.575,  # Home Run
    11: 0.364,  # Reached on error
    12: 0.364,  # Reached on error
    15: -0.407,
    16: -0.407
}

result_map = {
    0: [],  # Sour Left
    1: [],  # Nice Left
    2: [],  # Perfect
    3: [],  # Nice Right
    4: []   # Sour Right
}

print("Enter username of player (blank for all stats):")
user = input()
print("Enter '0' for stars-off data; '1' for stars-on")
stars = int(input())
print("Enter '0' for all data, '1' for ranked only")
ranked = int(input())

contact_url = "https://projectrio-api-1.api.projectrio.app/plate_data/?contact=0&contact=1&contact=2&contact=3&contact=4"
pitching_url = "https://projectrio-api-1.api.projectrio.app/detailed_stats/?exclude_batting=1&exclude_fielding=1&exclude_misc=1"

if stars == 0:
    contact_url += "&tag=Normal"
    pitching_url += "&tag=Normal"
elif stars == 1:
    contact_url += "&tag=Superstar"
    pitching_url += "&tag=Superstar"
if ranked == 1:
    contact_url += "&tag=Ranked"
    pitching_url += "&tag=Ranked"
if user != "":
    contact_url += "&users_as_pitcher=1&username=" + user
    pitching_url += "&username=" + user


plate_data = requests.get(contact_url).json()
pitching_data = requests.get(pitching_url).json()

pitching_stats = pitching_data["Stats"]["Pitching"]

# print(plate_data)
print(contact_url)

e_total = 0

for e in plate_data["Data"]:
    if e["type_of_swing"] == 2:
        if e["final_result"] != 0:
            e_total += 1
            result = 0
            if e["final_result"] in linear_weights:
                result = linear_weights[e["final_result"]]
                if result < 0:
                    result += 0.407
            result_map[e["type_of_contact"]].append(result)

e_total += pitching_stats["strikeouts_pitched"] + pitching_stats["walks_bb"] + pitching_stats["walks_hbp"]
re_total = 0

for result in result_map:
    re_total += sum(result_map[result])
    print("Result", result, "had an average result of", "{:.3f}".format(sum(result_map[result]) / len(result_map[result])), "in", len(result_map[result]), "events", "(" + "{:.2f}".format(len(result_map[result]) / e_total * 100) + "%)")

print("K%:", "{:.2f}".format(pitching_stats["strikeouts_pitched"] / e_total * 100))
print("BB%:", "{:.2f}".format((pitching_stats["walks_hbp"] + pitching_stats["walks_bb"]) / e_total * 100))
re_total += (pitching_stats["strikeouts_pitched"] * -0.407) + (pitching_stats["walks_bb"] * 0.336) + (pitching_stats["walks_hbp"] * 0.336)

print("Total expected runs allowed:", round(re_total), "Actual runs allowed:", pitching_stats["runs_allowed"])