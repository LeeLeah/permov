# coding: UTF-8

from . import *

class editMyAlbum(BaseHandler):
	@authenticated
	@gen.coroutine
	def get(self,cateId):
		user = self.current_user
		db = self.settings["db"]
		vipCheck = yield db.user.find_one({"user":user},{"vip":1})
		if vipCheck["vip"] > datetime.datetime.now():
			device = self.get_device()
			cate,messages= yield [db.cate.find_one({"user":user,"url":cateId}),
					self.getMessages(user)]
			if cate:
				self.render("editMyAlbum.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,
				cate=cate,messages=messages,user=user,userInfo=vipCheck,
				siteDomain=self.settings["siteDomain"])
			else:
				raise tornado.web.HTTPError(404)
		else:
			self.write("非VIP会员，没有画册功能。")

	@authenticated
	@gen.coroutine
	def post(self,cateId):
		user = self.current_user
		db = self.settings["db"]
		vipCheck = yield db.user.find_one({"user":user},{"vip":1})
		if vipCheck["vip"] > datetime.datetime.now():
			keywords = self.get_argument("keywords").split("+")[:7]
			name = self.get_argument("name")
			cateCheck = yield db.cate.find_and_modify(query={"user":user,"url":cateId},
				update={"$set":{"keywords":keywords,"title":self.get_argument("title"),
				"description":self.get_argument("description"),
				"name":name}},feilds={"name":1})
			if cateCheck["name"] != name:
				yield db.img.update({"cate_url":cateId},
					{"$set":{"cate":name}},multi=True)
			self.redirect("/myAlbum/")
		else:
			self.write("非VIP会员，没有画册功能。")

class myAlbum(BaseHandler):
	@authenticated
	@gen.coroutine
	def get(self):
		user = self.current_user
		db = self.settings["db"]
		vipCheck = yield db.user.find_one({"user":user},{"vip":1})
		if vipCheck["vip"] > datetime.datetime.now():
			device = self.get_device()
			cates,messages = yield [db.cate.find({"user":user}).to_list(40),
					self.getMessages(user)]
			
			self.render("myAlbum.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,
				cates=cates,messages=messages,user=user,userInfo=vipCheck,
				staticURL=self.settings["staticURL"],
				siteDomain=self.settings["siteDomain"])

		else:
			self.write("非VIP会员，没有画册功能。")


class addCate(BaseHandler):

	@authenticated
	@gen.coroutine
	def post(self):
		user = self.current_user
		db = self.settings["db"]
		name = self.get_argument("name")
		title = self.get_argument("title")
		description = self.get_argument("description")
		#try:
			#yield db.cateId.insert({"_id":"cateId","url":33})
		#except:
			#pass
		url = yield db.cateId.find_and_modify(query={"_id":"cateId"},
			update={"$inc":{"url":1}})
		yield db.cate.insert({"name":name,
			"user":user,
			"title":title,
			"description":description,
			"time":datetime.datetime.now(),
			"score":1,
			"url":str(url["url"]+1),
			"img":"","keywords":[]})
		self.redirect("/myAlbum/")
