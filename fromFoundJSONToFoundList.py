import json

with open("./foundV2.json", 'r', encoding='utf-8') as jsonF:
	with open("./found_listV2.txt", mode='a+', encoding='utf-8') as listF:
		for line in jsonF.readline()