import requests

print("Enter username of player (blank for all stats):")
user = input()
print("Enter '0' for stars-off data; '1' for stars-on")
stars = int(input())
print("Enter '0' for all data, '1' for ranked only")
ranked = int(input())

url = "https://projectrio-api-1.api.projectrio.app/detailed_stats/?exclude_batting=1&exclude_fielding=1&exclude_misc=1"
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

stats = response["Stats"]["Pitching"]
# batter avg vs pitcher
d_avg = stats["hits_allowed"] / (stats["batters_faced"]-stats["walks_bb"]-stats["walks_hbp"])
era = 9 * stats["runs_allowed"] / (stats["outs_pitched"] / 3)
# strikeout percentage
kp = (stats["strikeouts_pitched"] / stats["batters_faced"])*100

overall = all_response["Stats"]["Pitching"]
overall_davg = overall["hits_allowed"] / (overall["batters_faced"] - overall["walks_bb"] - overall["walks_hbp"])
overall_era = 9 * overall["runs_allowed"] / (overall["outs_pitched"] / 3)
overall_kp = (stats["strikeouts_pitched"] / stats["batters_faced"])*100
# character ERA-
cera_minus = ((era / overall_era)) * 100

print("opAVG / ERA / K%")

# not sure if overall is cERA or ERA, I assume the latter though
if user != "":
    print("OVERALL: " + "{:.3f}".format(d_avg) + " / " + "{:.2f}".format(era) + " / " + "{:.1f}".format(kp)+"%" + " / " + "{:.0f}".format(cera_minus) + " cERA-")
else:
    print("OVERALL: " + "{:.3f}".format(d_avg) + " / " + "{:.2f}".format(era) + " / " + "{:.1f}".format(kp) + "%" + " / " + "{:.0f}".format(cera_minus) + " ERA-")
url += "&by_char=1"

response = requests.get(url).json()
sorted_char_list = []
try:
    sorted_char_list = sorted(response["Stats"].keys(), key=lambda x: response["Stats"][x]["Pitching"]["batters_faced"], reverse=True)
except KeyError:
    print("There was an error sorting the character list")
    sorted_char_list = sorted(response["Stats"].keys())

for char in sorted_char_list:
    char_stats = response["Stats"][char]["Pitching"]
    if char_stats["batters_faced"] > 0 and char_stats["outs_pitched"] > 0:
        d_avg = char_stats["hits_allowed"] / (char_stats["batters_faced"] - char_stats["walks_bb"] - char_stats["walks_hbp"])
        era = 9 * char_stats["runs_allowed"] / (char_stats["outs_pitched"] / 3)
        kp = (char_stats["strikeouts_pitched"] / char_stats["batters_faced"])*100



        char_or_all = " cERA-"
        overall = all_char_response["Stats"][char]["Pitching"]
        if user == "":
            overall = all_response["Stats"]["Pitching"]
            char_or_all = " ERA-"
        overall_davg = overall["hits_allowed"] / (overall["batters_faced"] - overall["walks_bb"] - overall["walks_hbp"])
        overall_era = 9 * overall["runs_allowed"] / (overall["outs_pitched"] / 3)
        overall_kp = (overall["strikeouts_pitched"] / overall["batters_faced"])*100
        cera_minus = ((era / overall_era)) * 100
        print(char + " / " + "{:.0f}".format(char_stats["batters_faced"]) + " batter(s) faced" + " / " + "{:.3f}".format(d_avg) + " / " + "{:.2f}".format(era) + " ERA " " / " + "{:.1f}".format(kp) + "%" + " / " + str(round((cera_minus))) + char_or_all)
