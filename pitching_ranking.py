import requests

print("Enter name of character (blank for all stats):")
char = input()
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

if char != "":
    url += "&by_char=1"

total_response = requests.get(url).json()
print(url)

url += "&by_user=1"

user_response = requests.get(url).json()

user_dict = {}

overall = {}
if char == "":
    overall = total_response["Stats"]["Pitching"]
else:
    overall = total_response["Stats"][char]["Pitching"]

overall_avg = overall["hits_allowed"] / (overall["batters_faced"] - overall["walks_bb"] - overall["walks_hbp"])
overall_era = 9 * overall["runs_allowed"] / (overall["outs_pitched"] / 3)
overall_kp = (overall["strikeouts_pitched"] / overall["batters_faced"]) * 100
overall_outs = overall["outs_pitched"]
overall_ip = overall_outs // 3
overall_ip_str = str(overall_ip + (0.1 * (overall_outs % 3)))

for user in user_response["Stats"]:
    # todo
    stats = {}
    if char == "":
        stats = user_response["Stats"][user]["Pitching"]
    elif char in user_response["Stats"][user]:
        stats = user_response["Stats"][user][char]["Pitching"]
    else:
        pass
    if "batters_faced" in stats and "outs_pitched" in stats and stats["outs_pitched"] > 0:
        d_avg = stats["hits_allowed"] / (stats["batters_faced"] - stats["walks_bb"] - stats["walks_hbp"])
        era = 9 * stats["runs_allowed"] / (stats["outs_pitched"] / 3)
        kp = (stats["strikeouts_pitched"] / stats["batters_faced"]) * 100
        outs = stats["outs_pitched"]
        cera_minus = (era / overall_era) * 100
        user_dict[user] = (outs, d_avg, era, kp, cera_minus)

sorted_user_list = sorted(user_dict.keys(), key=lambda x: user_dict[x][4])

print("opp AVG / ERA / K%")
print("ALL (" + overall_ip_str + " IP): " + "{:.3f}".format(overall_avg) + " / " + "{:.2f}".format(overall_era) + " / " + "{:.1f}".format(overall_kp) + "%")

for user in sorted_user_list:
    outs = user_dict[user][0]
    d_avg = user_dict[user][1]
    era = user_dict[user][2]
    kp = user_dict[user][3]
    cera_minus = user_dict[user][4]
    ip_str = str((outs // 3) + (0.1 * (outs % 3)))
    c_o = " cERA-"
    if char == "":
        c_o = " ERA-"
    if (char != "" and outs > 100) or outs > 300:
        print(user + " (" + ip_str + " IP): " + "{:.3f}".format(d_avg) + " / " + "{:.2f}".format(era) + " / " + "{:.1f}".format(kp) + "%, " + str(round(cera_minus)) + c_o)
