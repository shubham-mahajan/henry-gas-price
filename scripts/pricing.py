from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import csv
import json
import datetime

# Output Directory Location
output_dir = '../data/'


"""
Method to create CSV from the JSON Data
@params 
	- json_data -> Contains Json Data
	- filename -> Name of the File for storage of CSV.
"""

def create_csv(json_data,filename):
	with open(f"{filename}.csv","w",newline="") as f:
		title = "Date,Price".split(",")
		cw = csv.DictWriter(f,title,delimiter=',')
		cw.writeheader()
		cw.writerows(json_data)


"""
Method to Format the Date for Daily Price Data
@params 
	- date -> Date in format of dd-MMM-YYYY
@return
	- formatted_date -> Date in format of YYYY-mm-dd
"""
def date_format_daily(date):
	formatted_date = datetime.datetime.strptime(date, '%d-%b-%Y').strftime('%Y-%m-%d')
	return formatted_date


"""
Method to Format the Date for Monthly Price Data
@params 
	- date -> Date in format of dd-mm-YYYY
@return
	- formatted_date -> Date in format of YYYY-mm-dd
"""
def date_format_monthly(date):
	formatted_date = datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
	return formatted_date


"""
Method to Fetch the Page from the URL
@params 
	- url -> URL of Location need to be Fetched
@return
	- BeautifulSoup Object
"""
def get_data(url):
	response = urlopen(url)
	return BeautifulSoup(response)


"""
Method to convert the Daily Price Data to CSV
"""
def daily_price_data():
	soap = get_data('https://www.eia.gov/dnav/ng/hist/rngwhhdd.htm')
	data = []
	price_data = soap.find("table", {"summary": "Henry Hub Natural Gas Spot Price (Dollars per Million Btu)"})
	for tr_row in price_data.findAll("tr"):
		dateString = tr_row.find("td", {"class": "B6"})
		if dateString:
			date_match = re.match(r'(\d{4})\s+(\w{3})-(\s?\d{1,2})', str(dateString.text.strip()))
			year = date_match[1]
			month = date_match[2]
			date = date_match[3].strip()
			date_format = f"{date}-{month}-{year}"
			current_date = date_format_daily(date_format)
			prices = tr_row.findAll("td", {"class": "B3"})
			for td_row in prices:
				data.append({
					"Date": current_date,
					"Price":td_row.text.strip()
				})
				format_date = datetime.datetime.strptime(str(current_date), "%Y-%m-%d")
				date_addition = format_date + datetime.timedelta(days=1)
				current_date = datetime.datetime.strftime(date_addition, "%Y-%m-%d")
	filename = f"{output_dir}henry_hub_gas_daily_price"
	create_csv(data,filename)

"""
Method to convert the Montly Price Data to CSV
"""
def monthly_price_data():
	soap = get_data('https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm')
	data = []
	price_data = soap.find("table", {"summary": "Henry Hub Natural Gas Spot Price (Dollars per Million Btu)"})
	for tr_row in price_data.findAll("tr"):
		dateString = tr_row.find("td", {"class": "B4"})
		if dateString:
			date_match = re.match(r'(\d{4})', str(dateString.text.strip()))
			year = date_match[1]
			prices = tr_row.findAll("td", {"class": "B3"})
			for (i,td_row) in enumerate(prices):
				date_ = f"1-{i+1}-{year}"
				current_date = date_format_monthly(date_)
				data.append({
					"Date": current_date,
					"Price":td_row.text.strip()
				})
	filename = f"{output_dir}henry_hub_gas_monthly_price"
	create_csv(data,filename)

if __name__ == "__main__":
	daily_price_data()
	monthly_price_data()