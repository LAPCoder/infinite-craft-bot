import json
import random
import requests
import os
import logging
from threading import Thread, Lock
from fake_useragent import UserAgent
from requests.packages.urllib3.exceptions import InsecureRequestWarning

FILE = "./foundV2.json"
LOGS = "./errors.log"
RANDOM_TYPE = 1
# 0 = default random, 1 = exponential random

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(filename=LOGS, encoding='utf-8')

file = open(FILE, "r", encoding='utf-8')
contents = file.read()
count = contents.count("result")
file.close()

file_lock = Lock()
print_lock = Lock()

with open("./proxies.json", 'r') as all_proxies_json:
	ALL_PROXIES = all_proxies_json.read()

def add(args, first, second):
	global count
	args["first"] = first
	args["second"] = second

	with file_lock:
		with open(FILE, 'rb+') as filehandle:
			filehandle.seek(-3, os.SEEK_END)
			filehandle.truncate()
		with open(FILE, mode='a+', encoding='utf-8') as feedsjson:
			feedsjson.write(",\n")
			json.dump(args, feedsjson, indent=4, ensure_ascii=False)
			feedsjson.write("\n]")

	count+=1

def request(first, second):
	proxy = {
		'http': random.choice( #https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt
			ALL_PROXIES
		)
	}

	headers = {
		'Host': 'neal.fun',
		'Referer': 'https://neal.fun/infinite-craft/',
		'Priority': 'u=1',
		'User-Agent': UserAgent().random,
		'X-Forwarded-For': f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
	}

	r = requests.get(
		"https://neal.fun/api/infinite-craft/pair?first="+first+"&second="+second,
		proxies=proxy,
		headers=headers,
		verify=False)

	with print_lock:
		print(r.status_code, end=" ")
		if r.status_code == 429:
			print("429 error")
			logging.critical("Recieved 429 error, can't continue: " + str(r.headers))
			exit(429)
		elif r.status_code != 200:
			print()
			al = r.text
			logging.warning(str(r.status_code) + ":" + al[al.find('<title>') + 7 : al.find('</title>')] + ": " + str(r.headers))
			return
		print(r.text)
	
	if r.text.find("Nothing") == -1:
		add(r.json(), first, second)

def do_it():
	try:
		#print("OK")
		if RANDOM_TYPE == 0:
			a = random.randint(0, count-1)
			b = random.randint(0, count-1)
		else:
			a = round(random.betavariate(1.3, 1) * count-1)
			b = round(random.betavariate(1.3, 1) * count-1)
			#print(count, a, b)
		with file_lock:
			with open(FILE, 'r', encoding='utf-8') as filehandle:
				jsonF = json.load(filehandle)
				aVal = jsonF[a]["result"]
				bVal = jsonF[b]["result"]
				if list(filter(lambda x: ((x.get('first') == aVal and x.get('second') == bVal) or (x.get('first') == bVal and x.get('second') == aVal)), jsonF)):
					#print("No redondance")
					return
		#print(aVal, bVal)
		request(aVal, bVal)
	except Exception as error:
		logging.error(error)
	finally:
		return

#request("Horn", "Fire")

while True:
	try:
		threads = [Thread(target=do_it) for _ in range(10)]
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()
	except KeyboardInterrupt:
		break
