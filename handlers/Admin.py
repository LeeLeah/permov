# coding: UTF-8

from . import *

class AddVipTime(BaseHandler):
	@authenticated
	@gen.coroutine
	@addslash
	def get(self):
		user = self.current_user
		if user == "***Admin_User***" or user == "**Administrator_User**":
			db = self.settings["db"]
			device = self.get_device()
			messages = yield self.getMessages(user)
			self.render("AddVipTime.html",user=user,
				siteURL=self.settings["siteURL"],device=device,
				messages=messages,siteDomain=self.settings["siteDomain"],
				siteName=self.settings["siteName"])
		else:
			raise tornado.web.HTTPError(404)

	@authenticated
	@gen.coroutine
	def post(self):
		user = self.current_user
		if user == "***Admin_User***" or user == "**Administrator_User**":
			db = self.settings["db"]
			vipDays = int(self.get_argument("month")) * 31
			timeNow = datetime.datetime.now()
			VipUser = self.get_argument("VipUser")
			check = yield db.user.find_one({"user":VipUser},{"vip":1})
			if check["vip"] > timeNow:
				vipTime = check["vip"] + datetime.timedelta(days=vipDays)
			else:
				vipTime = timeNow + datetime.timedelta(days=vipDays)
			yield db.user.update({"user":VipUser},{"$set":{"vip":vipTime}})
			self.redirect("/")
		else:
			raise tornado.web.HTTPError(404)

class AdminSuggest(BaseHandler):
	@authenticated
	@gen.coroutine
	@addslash
	def get(self):
		user = self.current_user
		if user == "***Admin_User***" or user == "**Administrator_User**":
			db = self.settings["db"]
			device = self.get_device()
			try:
				page = int(self.get_argument("page"))
			except:
				page = 1
			suggests,sugNum,messages = yield [db.suggest.find({"time":
				{"$gt":self.settings["gulipaTime"]}}
				).skip((page-1)*20).limit(20).to_list(20),
				db.suggest.count(),
				self.getMessages(user)]
			if sugNum % 20 == 0:
				pageNum = sugNum / 20
			else:
				pageNum = sugNum / 20 + 1
			self.render("AdminSuggest.html",suggests=suggests,user=user,
				siteURL=self.settings["siteURL"],device=device,messages=messages,
				siteDomain=self.settings["siteDomain"],page=page,
				siteName=self.settings["siteName"],pageNum=pageNum)
		else:
			raise tornado.web.HTTPError(404)
