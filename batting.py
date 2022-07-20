import requests

print("Enter username of player (blank for all stats):")
user = input()
print("Enter '0' for stars-off data; '1' for stars-on")
stars = int(input())
print("Enter '0' for all data, '1' for ranked only")
ranked = int(input())

url = "https://projectrio-api-1.api.projectrio.app/detailed_stats/?exclude_pitching=1&exclude_fielding=1&exclude_misc=1"
if stars == 0:
    url += "&tag=Normal"
elif stars == 1:
    url += "&tag=Superstar"
if ranked == 1:
    url += "&tag=Ranked"

all_response = requests.get(url).json()
all_char_response = requests.get(url + "&by_char=1").json()

if user != "":
    url += "&username=" + user

response = requests.get(url).json()

# print(response)

stats = response["Stats"]["Batting"]
o_avg = stats["summary_hits"] / stats["summary_at_bats"]
o_obp = (stats["summary_hits"] + stats["summary_walks_hbp"] + stats["summary_walks_bb"]) / stats["plate_appearances"]
o_slg = (stats["summary_singles"] + (stats["summary_doubles"] * 2) + (stats["summary_triples"] * 3) + (stats["summary_homeruns"] * 4)) / stats["summary_at_bats"]
o_ops = o_obp + o_slg
o_pa = stats["plate_appearances"]

overall = all_response["Stats"]["Batting"]
overall_obp = (overall["summary_hits"] + overall["summary_walks_hbp"] + overall["summary_walks_bb"]) / overall["plate_appearances"]
overall_slg = (overall["summary_singles"] + (overall["summary_doubles"] * 2) + (overall["summary_triples"] * 3) + (overall["summary_homeruns"] * 4)) / overall["summary_at_bats"]
ops_plus = ((o_obp / overall_obp) + (o_slg / overall_slg) - 1) * 100

print("AVG / OBP / SLG / OPS")
print("OVERALL (" + str(o_pa) + " PA): " + "{:.3f}".format(o_avg) + " / " + "{:.3f}".format(o_obp) + " / " + "{:.3f}".format(o_slg) + " / " + "{:.3f}".format(o_ops) + ", " + str(round(ops_plus)) + " OPS+")

url += "&by_char=1"

response = requests.get(url).json()
sorted_char_list = []
try:
    sorted_char_list = sorted(response["Stats"].keys(), key=lambda x: response["Stats"][x]["Batting"]["plate_appearances"], reverse=True)
except KeyError:
    print("There was an error sorting the character list")
    sorted_char_list = sorted(response["Stats"].keys())

# print(response)
for char in sorted_char_list:
    char_stats = response["Stats"][char]["Batting"]
    if char_stats["summary_at_bats"] > 0 and char_stats["plate_appearances"] > 0:
        avg = char_stats["summary_hits"] / char_stats["summary_at_bats"]
        obp = (char_stats["summary_hits"] + char_stats["summary_walks_hbp"] + char_stats["summary_walks_bb"]) / char_stats["plate_appearances"]
        slg = (char_stats["summary_singles"] + (char_stats["summary_doubles"] * 2) + (char_stats["summary_triples"] * 3) + (char_stats["summary_homeruns"] * 4)) / char_stats["summary_at_bats"]
        ops = obp + slg
        pa = char_stats["plate_appearances"]

        overall = all_char_response["Stats"][char]["Batting"]
        c_o = " cOPS+"
        if user == "":
            overall = all_response["Stats"]["Batting"]
            c_o = " OPS+"
        overall_obp = (overall["summary_hits"] + overall["summary_walks_hbp"] + overall["summary_walks_bb"]) / overall["plate_appearances"]
        overall_slg = (overall["summary_singles"] + (overall["summary_doubles"] * 2) + (overall["summary_triples"] * 3) + (overall["summary_homeruns"] * 4)) / overall["summary_at_bats"]
        ops_plus = ((obp / overall_obp) + (slg / overall_slg) - 1) * 100
        print(char + " (" + str(pa) + " PA): " + "{:.3f}".format(avg) + " / " + "{:.3f}".format(obp) + " / " + "{:.3f}".format(slg) + " / " + "{:.3f}".format(ops) + ", " + str(round(ops_plus)) + c_o)
