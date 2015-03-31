# coding: UTF-8

from . import *

class VIP(BaseHandler):
	@gen.coroutine
	def get(self):
		user = self.current_user
		db = self.settings["db"]
		if user:
			messages = yield self.getMessages(user)
		else:
			messages = 0
		siteName = self.settings["siteName"]
		siteURL = self.settings["siteURL"]
		siteDomain = self.settings["siteDomain"]
		device = self.get_device()
		self.render("vip.html",user=user,siteName=siteName,
				staticURL=self.settings["staticURL"],messages=messages,
				siteURL=siteURL,siteDomain=siteDomain,device=device)


class Message(BaseHandler):
	@authenticated
	@gen.coroutine
	def get(self):
		user = self.current_user
		device = self.get_device()
		if user:
			db = self.settings["db"]
			try:
				page = int(self.get_argument("page"))
			except:
				page = 1
			message,messages = yield [db.messages.find({"user":user,
				"time":{"$gt":self.settings["gulipaTime"]}}
				).skip((page-1)*20).limit(20).to_list(20),
				self.getMessages(user)]
			if messages % 20 == 0 :
				pageNum = messages / 20
			else:
				pageNum = messages / 20 + 1
			self.render("Message.html",message=message,user=user,
				siteURL=self.settings["siteURL"],device=device,messages=messages,
				siteDomain=self.settings["siteDomain"],page=page,
				siteName=self.settings["siteName"],pageNum=pageNum)


class Suggest(BaseHandler):
	@gen.coroutine
	def post(self):
		user = self.current_user
		db = self.settings["db"]
		description = self.get_argument("description")
		email = self.get_argument("email")
		if description :
			yield db.suggest.insert({
				"user":user,
				"description":description,
				"email":email,
				"time":datetime.datetime.now()
				})
		self.redirect(self.request.headers["referer"])

class Rule(BaseHandler):
	@gen.coroutine
	def get(self):
		user = self.current_user
		db = self.settings["db"]
		if user:
			messages = yield self.getMessages(user)
		else:
			messages = 0
		siteName = self.settings["siteName"]
		siteURL = self.settings["siteURL"]
		siteDomain = self.settings["siteDomain"]
		device = self.get_device()
		self.render("rule.html",user=user,siteName=siteName,
				staticURL=self.settings["staticURL"],messages=messages,
				siteURL=siteURL,siteDomain=siteDomain,device=device)
