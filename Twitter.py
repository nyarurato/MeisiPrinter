# -*- coding:utf-8 -*-
from requests_oauthlib import OAuth1Session
import json

class Twitter:
	def __init__(self):
		self.oathkeys = {
			"CK":"Input ConsumerKey",
			"CS":"Input ConsumerSecret",
			"AT":"Input AccessToken",
			"AS":"Input AccessTokenSecret"
		}

	def create_oath_session(self):
		oath = OAuth1Session(
			self.oathkeys["CK"],
			self.oathkeys["CS"],
			self.oathkeys["AT"],
			self.oathkeys["AS"]
		)
		return oath

	def get_user_info(self,username):
		url = "https://api.twitter.com/1.1/users/show.json"
		print("get_user @" + username)
		params = {
			"screen_name":username
		}
		oath = self.create_oath_session()
		responce = oath.get(url,params = params)
		if responce.status_code != 200:
			print("No user")
			print(responce.text)
			exit()
		userinfo = json.loads(responce.text)
		return userinfo