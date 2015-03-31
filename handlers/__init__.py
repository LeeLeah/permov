import tornado.web
from tornado.web import authenticated
from tornado import gen
import os
import datetime

class BaseHandler(tornado.web.RequestHandler):


	@gen.coroutine
	def getMessages(self,user):
		if user:
			messages = yield self.settings["db"].messages.find({"user":user},
				{"_id":1}).count()
		else:
			messages = 0
		raise gen.Return(messages)


	def get_current_user(self):
		
		return self.get_secure_cookie("user")

	def get_device(self):

		userAgent = self.request.headers["User-Agent"]

		return 0 if "Mobile" in userAgent or "Android" in userAgent else 1
