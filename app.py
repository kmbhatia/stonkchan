import requests
import pandas as pd
from nsetools import Nse
from io import StringIO
import logging
from configparser import ConfigParser
from datetime import datetime, date
import shelve
import os

config = ConfigParser()
config.read("config.ini")
auth = config['AUTH']["bot_key"]

today = date.today()
currentyear = datetime.now().year
day = datetime.today().strftime('%A')

logging.basicConfig(filename="/home/roark/stockchan/logfile.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.INFO)


if((today not in [str(currentyear)+'-01-26', str(currentyear)+'-08-15']) and (day not in ["Sunday","Saturday"])):
	
	topgainerarray=[]
	nse = Nse()
	top_gainers = nse.get_top_gainers()


	for index, element in enumerate(top_gainers, start=0):
			topgainerarray.append(element["symbol"])

	if(os.path.exists("/home/roark/stockchan/PreviousDayStats")):
		shelf = shelve.open("/home/roark/stockchan/PreviousDayStats", writeback = True)
	else:
		shelf = shelve.open("/home/roark/stockchan/PreviousDayStats", writeback = True)

	bool = True
	if("topgainers" not in shelf):
		shelf['topgainers'] = topgainerarray
	elif((shelf['topgainers']!= topgainerarray)):
		shelf['topgainers'] = topgainerarray
	elif(shelf['topgainers']==topgainerarray):
		bool = False

	shelf.close()

	if(bool):
		message = "Top Gainers of the Day"

		for scrip in topgainerarray:
			message+='\n'+scrip

		URL ="https://api.telegram.org/"+auth+"/sendMessage?chat_id=@stonkchan&text="+message
		response = requests.post(URL)
		logger.info(": Telegram Bot Response Status Code: "+str(response))

	else:
		URL ="https://api.telegram.org/"+auth+"/sendMessage?chat_id=@stonkchan&text= Markets haven't moved on account of Holiday."
		response = requests.post(URL)
		logger.info(": Telegram Bot Response Status Code: "+str(response))		

else:
	if(day in ["Sunday","Saturday"]):
		URL ="https://api.telegram.org/"+auth+"/sendMessage?chat_id=@stonkchan&text= Today is "+day+" hence the markets were closed."
	elif(today not in [str(currentyear)+'-01-26', str(currentyear)+'-08-15']):
		URL ="https://api.telegram.org/"+auth+"/sendMessage?chat_id=@stonkchan&text= Today is National Holiday hence the markets were closed."
	response = requests.post(URL)
	logger.info(": Telegram Bot - Markets Closed - Response Status Code: "+str(response))