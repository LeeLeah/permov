# coding: UTF-8

from . import *

class addKeyword(BaseHandler):
	@authenticated
	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		user = self.current_user
		imgId = self.get_argument("imgId")
		checkKeys = yield db.img.find_one({"_id":imgId},{"tags":1,"user":1})
		if len(checkKeys["tags"]) < 15 :
			keyword = self.get_argument("keyword")
			data = {"left":float(self.get_argument("left")),
						"top":float(self.get_argument("top")),
						"keyword":keyword}
			message = {
				"type":2,
				"imgId":imgId,
				"fromUser":user,
				"keyword":keyword,
				"user":checkKeys["user"],
				"time":datetime.datetime.now()}
			yield [db.img.update({"_id":imgId},{"$addToSet":{"tags":data}}),
				db.messages.insert(message)]
			self.redirect("/img/%s/" % imgId)
		else:
			self.write("该图片关键词数量已经达到15个，无法再添加。")


class addLink(BaseHandler):
	@authenticated
	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		user = self.current_user
		checkVIP = yield db.user.find_one({"user":user},{"vip":1})
		if checkVIP["vip"] > datetime.datetime.now():
			imgId = self.get_argument("imgId")
			checkLinks = yield db.imgLink.find({"imgId":imgId},{"_id"}).count()
			if checkLinks < 10:
				url = self.get_argument("url")
				description = self.get_argument("description")
				data = {"user":user,"left":float(self.get_argument("left")),
							"top":float(self.get_argument("top")),
							"imgId":imgId,
							"url":url,
							"description":description}
				message = {
					"user":self.get_argument("toUser"),
					"type":3,
					"fromUser":user,
					"url":url,
					"imgId":imgId,
					"description":description,
					"time":datetime.datetime.now()}
				yield [db.imgLink.insert(data),
					db.messages.insert(message)]	
				self.redirect("/img/%s/" % imgId)
			else:
				self.write("此图片链接数量已达到10个，无法再添加。")
		else:
			self.write("非VIP会员，无法使用此功能。")

class next(BaseHandler):
	@gen.coroutine
	def get(self,img_url):
		db = self.settings["db"]
		device = self.get_device()
		thisImg = yield db.img.find_one({"_id":img_url},{"time":1,"cate_url":1})
		if thisImg:
			nextImg = yield db.img.find_one({"cate_url":thisImg["cate_url"],
				"time":{"$lt":thisImg["time"]}})
			if nextImg:
				self.redirect("/img/%s/" % nextImg["_id"])
			else:
				self.redirect("/%s/" % thisImg["cate_url"])
		else:
			raise tornado.web.HTTPError(404)
			
class comment(BaseHandler):
	def get(self):
		raise tornado.web.HTTPError(404)

	@authenticated
	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		user = self.current_user
		description = self.get_argument("description")
		if description:
			imgId = self.get_argument("imgId")
			timeNow = datetime.datetime.now()
			try:
				replyUser = self.get_argument("replyUser")
			except:
				replyUser = ""
			if replyUser:
				yield [db.comments.insert({"description":description,
							"imgId":imgId,"time":timeNow,
							"user":user,"replyUser":replyUser
							}),
					db.messages.insert([{"type":4,"fromUser":user,
							"user":self.get_argument("toUser"),
							"imgId":imgId,"time":timeNow,
							"description":description},
							{"type":5,"fromUser":user,"user":replyUser,
							"imgId":imgId,"time":timeNow,
							"description":description}])]
			else:
				yield [db.comments.insert({"description":description,
							"imgId":imgId,"time":timeNow,
							"user":user,"replyUser":replyUser
							}),
					db.messages.insert({"type":4,"fromUser":user,
							"user":self.get_argument("toUser"),
							"imgId":imgId,"time":timeNow,
							"description":description
							})]
		self.redirect(self.request.headers["referer"])


class img(BaseHandler):

	@gen.coroutine
	def get(self,img_url):
		db = self.settings["db"]
		user = self.current_user
		device = self.get_device()
		imgInfo = yield db.img.find_and_modify(
			query={"_id":img_url},
			update={"$inc":{"views":1}})
		if imgInfo:
			userInfo,imgLink,comments = yield [db.user.find_one({
				"user":imgInfo["user"]},{"avatar":1}),
			db.imgLink.find({"imgId":imgInfo["_id"]}).limit(10).to_list(10),
			db.comments.find({"imgId":imgInfo["_id"],
				"time":{"$gt":self.settings["gulipaTime"]}}).to_list(20)]
			if not user:
				FollowCheck = None
				messages = 0
			else:
				FollowCheck,messages = yield [db.user.find_one({"user":user,
				"FollowUser":imgInfo["user"]},{'_id':1}),
				self.getMessages(user)]
			
			self.render("img.html",user=user,FollowCheck=FollowCheck,
				siteName=self.settings["siteName"],userInfo=userInfo,
				siteURL=self.settings["siteURL"],device=device,
				staticURL=self.settings["staticURL"],imgLink=imgLink,
				comments=comments,messages=messages,
				siteDomain=self.settings["siteDomain"],imgInfo=imgInfo)
		else:
			raise tornado.web.HTTPError(404)

class category(BaseHandler):

	@gen.coroutine
	def get(self,cate_url):
		db = self.settings["db"]
		device = self.get_device()
		user = self.current_user
		try:
			page = int(self.get_argument("page"))
		except:
			page = 1
		imgInfo,imgCount,FollowNum,cate= yield [db.img.find({"cate_url":cate_url,
			"time":{"$gt":self.settings["gulipaTime"]}
				},{"description":1}).skip((page-1)*20).limit(20).to_list(20),
				db.img.find({"cate_url":cate_url}).count(),
				db.user.find({"FollowCate":cate_url}).count(),
				db.cate.find_one({"url":cate_url})]
		if not user :
			CateCheck = None
			messages = 0
		else:
			CateCheck,messages = yield [db.user.find_one({"user":user,
					"FollowCate":cate_url}),
				self.getMessages(user)]
		if imgCount % 20 == 0 :
			pageNum = imgCount / 20
		else:
			pageNum = imgCount / 20 + 1

		self.render("cate.html",user=user,CateCheck=CateCheck,FollowNum=FollowNum,
				siteName=self.settings["siteName"],cate=cate,messages=messages,
				staticURL=self.settings["staticURL"],cate_url=cate_url,imgCount=imgCount,
				siteURL=self.settings["siteURL"],pageNum=pageNum,page=page,
				siteDomain=self.settings["siteDomain"],imgInfo=imgInfo,device=device)

