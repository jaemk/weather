#!/home/james/projects/weather/forecast/bin/python

import os,sys,time,datetime
from multiprocessing import Process, Queue
from dateutil import tz
import requests
import json

from_zone = tz.gettz("UTC")
to_zone =tz.gettz("America/New_York")

with open("api.conf") as f:
	line = f.readline()
	if line != '':
		api = (line.strip().strip('"').strip("'"))
# input(str(api) + str(type(api)))

url = "https://api.forecast.io/forecast/%s/%s,%s"

loc_lat = "39.95"
loc_long = "-75.1667"
cel = '\u00b0'


class Updater(object):
	line = ''
	words = '   Fetching info '
	def __init__(self):
		sys.stdout.write("\n\n")

	def update(self):
		if len(self.line) < 20:
			self.line+='.'
		else:
			sys.stdout.write("\r"+' '*(len(self.words)+len(self.line)) )
			self.line = ''
		sys.stdout.write("\r"+self.words+self.line)
		time.sleep(.05)


def get_weather(q):
	query = url %(api, loc_lat, loc_long)
	r = requests.get(query)

	if r.status_code != 200:
		print("Error: ", r.status_code)
	else:
		weather = r.json()

	q.put(weather)

def getting_weather():
	os.system("clear")
	u = Updater()
	q = Queue()
	p = Process(target=get_weather, args=(q,))
	p.start()
	while p.is_alive() == True:
		u.update()
	weather = q.get()
	p.join()
	return weather


def refreshed():
	line = '  ** Refresh successful! **'
	delete = ' '*len(line)
	sys.stdout.write('\n\n\t'+line)
	time.sleep(1)
	sys.stdout.write('\r\t'+delete)

def fix_timezone(stamp):
	utc = datetime.datetime.utcfromtimestamp(stamp)
	utc = utc.replace(tzinfo=from_zone)
	etc = utc.astimezone(to_zone)
	return etc

def clock(stamp,hand=""):
	if hand == "hour":
		val = str(stamp.hour)
	elif hand == "minute":
		val = str(stamp.minute)
	else:
		return "00"

	if len(val) < 2:
		val+='0'
		val = val[::-1]

	return val


def show_current(weather):
	current = weather['currently']
	daily = weather['daily']['data'][0]
	cur_time = fix_timezone(current['time'])
	sr_time = fix_timezone(daily['sunriseTime'])
	ss_time = fix_timezone(daily['sunsetTime'])
	os.system("clear")
	print("Overall Forecast:", daily['icon']) 
	print("\n\t      Date: " + str(cur_time.month) + "/" + str(cur_time.day) + " - " + clock(cur_time, hand="hour") + ":" + clock(cur_time, hand="minute")\
		+ "\n\t            Rise: " + clock(sr_time, hand="hour") + ":" + clock(sr_time, hand="minute")\
		+ "\n\t             Set: " + clock(ss_time, hand="hour") + ":" + clock(ss_time, hand="minute")\
		+ "\n\t Currently: " + current['summary'] + ","\
		+ "\n\t            " + daily['summary']\
		+ "\n\tFeels Like: " + str(round(current['apparentTemperature'],1)) + " degF, "+ str(round((current['apparentTemperature']-32.0)*(5.0/9.0),1))+" degC"\
		+ "\n\t  Humidity: " + str(round(current['humidity']*100.0,1)) + "%"\
		+ "\n\t Dew Point: " + str(round(current['dewPoint'],1)) + " degF"\
		+ "\n\tNearest Storm: " + str(current['nearestStormDistance']) + " miles" )
	# print(current.keys()) 

# hourly = weather['hourly']
# hkeys = hourly.keys()
# print("\nToday's Forecast: ",hourly['icon'])
# hdata = hourly['data']
# for dat in hdata:
# 	hutc = datetime.datetime.utcfromtimestamp(dat['time'])
# 	hutc = hutc.replace(tzinfo=from_zone)
# 	hetc = hutc.astimezone(to_zone)
# 	print("\t"+str(hetc.month)+"/"+str(hetc.day)+" - "+str(hetc.hour)+":"+str(hetc.minute)+" -> Feels Like: "+str(dat['apparentTemperature']) + "degF, "+str(round((dat['apparentTemperature']-32)*(5.0/9.0),1)) +"degC")

def main():
	while True:
		weather = getting_weather()
		# input(weather['daily']['data'][0])
		show_current(weather)
		refreshed()
		ans = input("\n\t(Enter) to Refresh, (e) to Exit...")
		if ans.strip().lower() == 'e':
			break 



if __name__ == "__main__":
	main()

