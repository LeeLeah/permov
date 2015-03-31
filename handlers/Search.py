# coding: UTF-8

from . import *
import urllib
import chardet

class search(BaseHandler):

	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		device = self.get_device()
		keyword = urllib.quote(self.get_argument("keyword").encode("utf-8"))
		if keyword:
			self.redirect("/tag/%s/" % keyword)
		else:
			raise self.redirect("/")

class tags(BaseHandler):

	@gen.coroutine
	def get(self,keyword):
		try:
			page = int(self.get_argument("page"))
		except:
			page = 1
		try:
			db = self.settings["db"]
			imgInfo,imgNum= yield [db.img.find({"tags.keyword":
				keyword,"views":{"$gt":0}
				}).skip((page-1)*20).limit(20).to_list(20),
				db.img.find({"tags.keyword":keyword}).count()]
			if imgNum % 20 == 0:
				pageNum = imgNum/20
			else:
				pageNum = imgNum/20 + 1
			user = self.current_user
			device = self.get_device()
			if user:
				messages = yield self.getMessages(user)
			else:
				messages = 0
			self.render("search.html",user=self.get_current_user,
				siteName=self.settings["siteName"],keyword=keyword,
				siteURL=self.settings["siteURL"],device=device,messages=messages,
				staticURL=self.settings["staticURL"],page=page,pageNum=pageNum,
				siteDomain=self.settings["siteDomain"],imgInfo=imgInfo)
		except Exception,E:
			raise tornado.web.HTTPError(404)
