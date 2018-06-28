import serial
import urllib.request, json
import sys
import requests
from time import sleep, time
API_ENDPOINT = "http://127.0.0.1:3000/api"
while True:
    data = {}
    pre_time = time()
    with urllib.request.urlopen("http://192.168.10.3:8080/data/aircraft.json") as url:
        adsb = []
        data = json.loads(url.read().decode())
        print("read json aircraft..")
        for aircraft in data['aircraft']:
            aircraft['unixtime'] = data['now']
            aircraft['node_number'] = 1
            if all(x in aircraft for x in ("lat","lon","flight","altitude")):
                res = requests.post(url = API_ENDPOINT, data = aircraft)
                print("status : "+str(res))
                print(str(aircraft['unixtime'])+" send "+str(time()))
    print("1 jps(json per second) file in " + str(time()-pre_time) +" seconds")
    sleep(1)
