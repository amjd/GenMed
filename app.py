import os
import urllib
import json
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

TXTWEB_APP_KEY = os.environ['TXTWEB_APP_KEY']

class TrueMD(object):

	def __init__(self):
		self.ENDPOINT = "http://www.truemd.in/api/"
		self.API_KEY = os.environ['API_KEY']
		self.params = {}

	def __params(self, search_term, limit = None):
		self.params['id'] = search_term
		self.params['key'] = self.API_KEY
		if limit:
			self.params['limit'] = limit
		print repr(self.params)

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
			request = requests.get(url, params=self.params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				error_code = 0
				error_msg = "Success"
				temp_list = result['response']['suggestions']
				suggestions_list = [item['suggestion'] for item in temp_list]

		except:
			error_code = 1
			error_msg = "Sorry, we are experiencing some connection issues right now. Please try again later."
		return suggestions_list, error_code, error_msg

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
			request = requests.get(url, params=self.params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				medicine_details = result['response']
			return medicine_details
		except:
			return medicine_details

	def med_alternatives(self, search_term, limit = 5):
		"""
		GET /medicine_alternatives
		Parameters:
		id = SEARCH_STRING, key = API_KEY, limit = LIMIT
		"""
		url = self.ENDPOINT + 'medicine_alternatives/'
		self.__params(search_term, limit)
		alternatives_list = []
		try:
			request = requests.get(url, params=self.params)
			result = request.json()
			if result['status'] == 'ok' or result['status'] == 200:
				temp_list = result['response']['medicine_alternatives']
				alternatives_list = [{'brand': item['brand'], 'unit_price' : item['unit_price']} for item in temp_list]
				error_code = 0
				error_msg = "Success"
		except:
			error_code = 1
			error_msg = "Sorry, we are experiencing some connection issues right now. Please try again later."

		return alternatives_list, error_code, error_msg

@app.route('/app/med_sugg')
def med_sugg():
	message = request.args['txtweb_message'].strip()
	tmd = TrueMD()
	suggestions, error_code, error_msg = tmd.med_suggestions(message)
	if suggestions:
		return render_template("suggestions.html", suggestions=suggestions, error_code=error_code, \
			error_msg=error_msg, txtweb_key=TXTWEB_APP_KEY)
	else:
		error_code = 2
		error_msg = "We couldn't find a medicine by that name."
		return render_template("suggestions.html", suggestions=suggestions, error_code=error_code, \
			error_msg=error_msg, txtweb_key=TXTWEB_APP_KEY)

#UNFINISHED
@app.route('/app/med_detl')
def med_detl():
	message = request.args['txtweb_message'].strip()
	tmd = TrueMD()
	details = tmd.med_details(message)
	result = ""
	if details:
		for suggestion in suggestions:
			result = result + '<a href="/app/med_alt/%s">%s</a>\n' % (suggestion, suggestion)
	else:
		result = "We couldn't find a medicine by that name."

	return render_template("suggestions.html", result=result.split('\n'), txtweb_key=TXTWEB_APP_KEY)

@app.route('/app/med_alt/<med_name>')
def med_alt(med_name):
	med_name = urllib.unquote(med_name.encode('ascii')).decode('utf-8')
	print med_name
	tmd = TrueMD()
	alternatives, error_code, error_msg = tmd.med_alternatives(med_name)
	if alternatives:
			return render_template("alternatives.html", alternatives=alternatives, error_code=error_code, \
			error_msg=error_msg, txtweb_key=TXTWEB_APP_KEY)
	else:
		error_code = 2
		error_msg = "We couldn't find a generic alternative for that medicine."
		return render_template("suggestions.html", suggestions=suggestions, error_code=error_code, \
			error_msg=error_msg, txtweb_key=TXTWEB_APP_KEY)

if __name__ == '__main__':
	app.run(debug=True)
