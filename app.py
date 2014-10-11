import requests
import json
import os
from flask import Flask, request, render_template

app = Flask(__name__)

TXTWEB_APP_KEY = os.environ['TXTWEB_APP_KEY']

class TrueMD(object):
	ENDPOINT = "http://www.truemd.in/api/"
	API_KEY = os.environ['API_KEY']

	def __init__(self):
		self.params = {}

	def __params(self, search_term, limit = None):
		self.params['id'] = search_term
		self.params['key'] = self.API_KEY
		if limit:
			self.params['limit'] = limit

	def med_suggestions(self, search_term, limit = 5):
		"""
		GET /medicine_suggestions
		Parameters:
		id = SEARCH_STRING, key = API_KEY, limit = LIMIT
		"""
		url = self.ENDPOINT + 'medicine_suggestions/'
		self.__params(search_term, limit)
		suggestions_list = []
		try:
			request = requests.get(url, params=params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				for item in result['response']['suggestions']:
					suggestions_list.append(item['suggestion'])
			return suggestions_list
		except:
			return suggestions_list

	def med_details(self, search_term):
		"""
		GET /medicine_details
		Parameters:
		id = SEARCH_STRING, key = API_KEY
		"""
		url = self.ENDPOINT + 'medicine_details/'
		self.__params(search_term)
		medicine_details = {}
		try:
			request = requests.get(url, params=params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				medicine_details = result['response']
			return medicine_details
		except:
			return medicine_details

	def med_alternatives(self search_term, limit = 5):
		"""
		GET /medicine_alternatives
		Parameters:
		id = SEARCH_STRING, key = API_KEY, limit = LIMIT
		"""
		url = self.ENDPOINT + 'medicine_alternatives/'
		self.__params(search_term, limit)
		alternatives_list = []
		try:
			request = requests.get(url, params=params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				for item in result['response']['medicine_alternatives']:
					alternatives_list.append(item)
			return alternatives_list
		except:
			return alternatives_list			

@app.route('/app')
def index():
	message = request.args['txtweb_message'].strip()
	tmd = TrueMD()
	suggestions = tmd.med_suggestions(message)
	result = ""
	if suggestions:
		result = "Did you mean:<br>"
		for suggestion in suggestion:
			result = result + '<a href="/app/med_alt/%s">%s</a><br>' % (suggestion, suggestion)
	else:
		result = "We couldn't find a medicine by that name."

	return render_template("based.html", result=result, textweb_key = TXTWEB_APP_KEY)

@app.route('/app/med_alt/<med_name>')
def med_alt(med_name):
	tmd = TrueMD()
	alternatives = tmd.med_alternatives(med_name)
	result = ""
	if alternatives:
		result = "Equivalent generic medicines:<br>"
		for alternative in alternatives:
			result = result + "%s [Unit price: Rs. %s]<br>" % (alternative['brand'], alternative['unit_price'])
	else:
		result = "We couldn't find a generic alternative for that medicine"
		
	return render_template("based.html", result=result, textweb_key = TXTWEB_APP_KEY)

if __name__ == '__main__':
	app.run(debug=True)
