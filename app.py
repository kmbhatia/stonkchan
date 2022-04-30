import requests
from nsetools import Nse
from io import StringIO
import logging
from configparser import ConfigParser
from datetime import datetime, date
import shelve
import os
import re

config = ConfigParser()
config.read("config.ini")
auth = config['AUTH']["bot_key"]
pwd = config["AUTH"]["pwd"]


today = date.today()
currentyear = datetime.now().year
day = datetime.today().strftime('%A')

logging.basicConfig(filename=pwd+"/logfile.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.INFO)


if((today not in [str(currentyear)+'-01-26', str(currentyear)+'-08-15']) and (day not in ["Sunday","Saturday"])):
	nse = Nse()
	parentarray=[]
	parentarray.append(nse.get_top_gainers())
	parentarray.append(nse.get_top_losers())
	message =""

	if(os.path.exists(pwd+"/PreviousDayStats")):
		shelf = shelve.open(pwd+"/PreviousDayStats", writeback = True)
	else:
		shelf = shelve.open(pwd+"/PreviousDayStats", writeback = True)

	bool = True
	if("topgainers" not in shelf):
		shelf['topgainers'] = nse.get_top_gainers()
	elif((shelf['topgainers']!= nse.get_top_gainers())):
		shelf['topgainers'] = nse.get_top_gainers()
	elif(shelf['topgainers']==nse.get_top_gainers()):
		bool = False

	if("toplosers" not in shelf):
		shelf['toplosers'] = nse.get_top_losers()
	elif((shelf['toplosers']!= nse.get_top_losers())):
		shelf['toplosers'] = nse.get_top_losers()

	shelf.close()

	
	for index, parent in enumerate(parentarray):
		gainerloserarray=[]
		print(index)
		for element in parent:
			object = {}
			object["symbol"] = element['symbol']
			object["ltp"] = element['ltp']
			object["percentagegains"] = round(((element['ltp']-element['previousPrice'])/element['previousPrice'])*100, 2)
			if(len(gainerloserarray)<5):
				gainerloserarray.append(object)
		print(gainerloserarray)
		
		if(bool):
			if(index == 0):
				message += "Top Gainers of the Day \n"
			else:
				message += "\n \n Top Losers of the Day \n"
			for scrip in gainerloserarray:
				message+='\n'+scrip['symbol']+': '+str(scrip['ltp'])+'('+str(scrip['percentagegains'])+'%) \n'
			message = message.replace("&", "%26")
		else:
			message = "Markets haven't moved on account of Holiday."

else:
	if(day in ["Sunday","Saturday"]):
		message = "Today is "+day+" hence the markets were closed."
	elif(today in [str(currentyear)+'-01-26', str(currentyear)+'-08-15']):
		message = "Today is National Holiday hence the markets were closed."


URL ="https://api.telegram.org/"+auth+"/sendMessage?chat_id=@stonkchan&text="+message
response = requests.post(URL)
logger.info(": Telegram Bot Response Status Code: "+str(response))
