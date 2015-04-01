# coding: UTF-8

from . import *
import hashlib
from tornado.httpclient import AsyncHTTPClient
from bson import ObjectId

class delComment(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		user = self.current_user
		db = self.settings["db"]
		yield db.comments.remove({"_id":ObjectId(self.get_argument("commentId")),
			"user":user})

class QQ(BaseHandler):

	@gen.coroutine
	@addslash
	def get(self):
		db = self.settings["db"]
		code = self.get_argument("code")
		state = self.get_argument("state")
		assert state == self.get_cookie("_xsrf")
		token_url = "https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=***QQ_CLIENT_ID***&client_secret=***CLIENT_SECRET***&code=%s&redirect_uri=http://www.permov.com/qq/"\
						% code
		get_token = yield AsyncHTTPClient().fetch(token_url)
		access_token = get_token.body.split("&")[0].split("=")[-1]
		openid_url = "https://graph.qq.com/oauth2.0/me?access_token=%s" % access_token
		get_openid = yield AsyncHTTPClient().fetch(openid_url)
		openid = get_openid.body.split('":"')[-1].split('"')[0]
		user = yield db.user.find_one({"QQOpenId":openid},{"user":1,"email":1})
		if user:
			if user["user"]:
				self.set_secure_cookie("user",user["user"])
				self.redirect("/")
		else:
			device = self.get_device()
			action = "QQ登录授权成功，请绑定您的喷沫屋账号，完成授权。"
			self.render("Bunding.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,action=action,
				siteDomain=self.settings["siteDomain"],QQOpenId=openid,user="",
				staticURL=self.settings["staticURL"],color=1,messages=0)

	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		QQOpenId = self.get_argument("QQOpenId")
		user = self.get_argument("user")
		password = hashlib.sha1(self.get_argument("password")).hexdigest()
		check = yield db.user.find_one({"user":user,"password":password})
		if check:
			yield db.user.update({"user":user},{"$set":{"QQOpenId":QQOpenId}})
			self.set_secure_cookie("user",user)
			self.redirect("/")
		else:
			device = self.get_device()
			action = "账号或密码错误，绑定失败！请重新绑定！"
			self.render("Bunding.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,action=action,
				siteDomain=self.settings["siteDomain"],QQOpenId=QQOpenId,user="",
				staticURL=self.settings["staticURL"],color=0)


class UserPage(BaseHandler):
	@gen.coroutine
	@addslash
	def get(self,pageuser):
		userAgent = self.request.headers["User-Agent"]
		device = 0 if "Mobile" in userAgent or "Android" in userAgent else 1	
		user = self.current_user
		db = self.settings["db"]
		PageUserInfo = yield db.user.find_one({"user":pageuser},
			{"avatar":1})
		if PageUserInfo:
			try:
				page = int(self.get_argument("page"))
			except:
				page = 1
			imgInfo,imgCount,FollowNum = yield [
				db.img.find({"user":pageuser,"views":{"$gt":0}}
					).skip((page-1)*20).limit(20).to_list(20),
				db.img.find({"user":pageuser}).count(),
				db.user.find({"FollowUser":pageuser}).count()]
			if user :
				UserCheck,messages= yield [db.user.find_one({"user":user,
					"FollowUser":pageuser}),
					self.getMessages(user)]
			else:
				UserCheck = 0
				messages = 0

			if imgCount % 20 == 0:
				pageNum = imgCount / 20
			else:
				pageNum = imgCount / 20 + 1

			self.render("UserPage.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,pageuser=pageuser,
				page=page,siteDomain=self.settings["siteDomain"],
				PageUserInfo=PageUserInfo,imgCount=imgCount,UserCheck=UserCheck,
				FollowNum=FollowNum,imgInfo=imgInfo,user=user,messages=messages,
				pageNum=pageNum,staticURL=self.settings["staticURL"])

		else:
			raise tornado.web.HTTPError(404)


class home(BaseHandler):
	@authenticated
	@gen.coroutine
	@addslash
	def get(self):
		db = self.settings["db"]
		user = self.current_user
		device = self.get_device()
		userInfo,messages = yield [db.user.find_one({"user":user},{"FollowCate":1,
			"FollowUser":1,"avatar":1,"vip":1}),
				self.getMessages(user)]
		if userInfo:
			try:
				page = int(self.get_argument("page"))
			except:
				page = 1
			imgInfo,newInfo,imgNum = yield [db.img.find({
				"time":{"$gt":self.settings["gulipaTime"]},
				"$or":[{"user":{"$in":userInfo["FollowUser"]}},
				{"cate_url":{"$in":userInfo["FollowCate"]}}]}
				).skip((page-1)*20).limit(20).to_list(20),
				db.img.find({"views":{"$gt":2}}).limit(5).to_list(5),
				db.img.find({"$or":[
					{"user":{"$in":userInfo["FollowUser"]}},
					{"cate_url":{"$in":userInfo["FollowCate"]}}]}
					).count()]
			if imgNum % 20 == 0 :
				pageNum = imgNum / 20
			else:
				pageNum = imgNum / 20 + 1

			self.render("home.html",siteName=self.settings["siteName"],userInfo=userInfo,
					siteURL=self.settings["siteURL"],device=device,user=user,messages=messages,
					page=page,siteDomain=self.settings["siteDomain"],newInfo=newInfo,
					imgInfo=imgInfo,pageNum=pageNum,staticURL=self.settings["staticURL"])
		else:
			self.clear_cookie("user")
			self.redirect("/")


class editImg(BaseHandler):
	@authenticated
	@gen.coroutine
	@addslash
	def get(self,imgId):
		db = self.settings["db"]
		user = self.current_user
		device = self.get_device()
		vipCheck = yield db.user.find_one({"user":user},{"vip":1})
		if vipCheck["vip"] < datetime.datetime.now():
			info = yield db.img.find_one({"_id":imgId,"user":user})
			checkResult = 1 if info else 0
		else:
			checkResult = 1
			info = yield db.img.find_one({"_id":imgId})
		if checkResult :
			cate = self.get_cookie("cate")
			cate_url = self.get_cookie("cate_url")
			messages,mycates = yield [self.getMessages(user),
				db.cate.find({"$or":[{"user":user},{"user":"幸运的炮灰"}]},
					{"name":1,"url":1}).to_list(40)]
			self.render("editImg.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,user=user,
				cate=cate,cate_url=cate_url,info=info,messages=messages,
				siteDomain=self.settings["siteDomain"],mycates=mycates)
		else:
			self.write("对不起，您还不是VIP会员，无法修改其他用户的图片。")

	@authenticated
	@gen.coroutine
	def post(self,imgId):
		db = self.settings["db"]
		user = self.get_argument("user")
		description = self.get_argument("description")
		vipCheck,userCheck = yield [db.user.find_one({"user":user},{"vip":1}),
						db.img.find_one({"_id":imgId},{"user":1})]
		if vipCheck["vip"] < datetime.datetime.now():
			checkResult = 1 if userCheck["user"] == user else 0
		else:
			checkResult = 1

		if checkResult:
			messageCheck = 0 if user != userCheck["user"] else 1
			data = {
				"cate_url":self.get_argument("cate_url"),
				"description":description}
			if int(data["cate_url"]) > 33:
				dataCate = yield db.cate.find_and_modify(query={"user":user,"url":data["cate_url"]},
				feilds={"name":1},update={"$set":{"img":imgId},"$inc":{"score":1}})
			else:
				dataCate = yield db.cate.find_and_modify(query={"url":data["cate_url"]},
				feilds={"name":1},update={"$set":{"img":imgId},"$inc":{"score":1}})
			data["cate"] = dataCate["name"]
			if messageCheck:
				yield db.img.update({"_id":imgId},{"$set":data})
			else:
				yield [db.img.update({"_id":imgId},{"$set":data}),
						db.messages.insert({
							"type":6,
							"imgId":imgId,
							"description":description,
							"fromUser":user,
							"user":userCheck["user"],
							"time":datetime.datetime.now()
							})]
			self.set_cookie("cate",data["cate"])
			self.set_cookie("cate_url",data["cate_url"])
			try:
				avatar = self.get_argument("avatar")
				yield db.user.update({"user":user},{"$set":{"avatar":imgId}})
			except:
				pass

			self.redirect("/img/%s/" % imgId)
		else:
			raise tornado.web.HTTPError(404)

class Reg(BaseHandler):
	@addslash
	def get(self):
		user = self.current_user
		if user :
			self.redirect("/")
		device = self.get_device()

		self.render("reg.html",siteName=self.settings["siteName"],
			siteURL=self.settings["siteURL"],device=device,user=user,
			siteDomain=self.settings["siteDomain"],action=None,messages=0)

	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		password = hashlib.sha1(self.get_argument("password")).hexdigest()
		user = self.get_argument("user")
		email = self.get_argument("email")
		device = self.get_device()
		ref = self.get_cookie("ref")
		data = {"user":user,"FollowUser":[user,"幸运的炮灰"],
				"email":email,"FollowCate":[],
				"vip":datetime.datetime.now() + datetime.timedelta(days=31),
				"avatar":"","QQOpenId":"","ref":ref,
				"password":password}
		if user and email:
			try:
				yield db.user.insert(data)
				self.set_secure_cookie("user",user)
				if ref:
					vipCheck = yield db.user.find_one({"user":ref},{"vip":1})
					timeNow = datetime.datetime.now()
					if vipCheck["vip"] > timeNow:
						vipTime = vipCheck["vip"] + datetime.timedelta(days=31)
					else:
						vipTime = timeNow + datetime.timedelta(days=31)
					yield db.user.update({"user":ref},{"$set":{"vip":vipTime}})
				self.redirect(self.request.headers["referer"])
			except:
				action = "登录账号或邮箱地址已被占用，请重新注册！"
				self.render("reg.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,user=user,
				siteDomain=self.settings["siteDomain"],action=action,messages=0)

		else:
			action = "登录账号或邮箱地址不能为空，请重新注册！"
			self.render("reg.html",siteName=self.settings["siteName"],
			siteURL=self.settings["siteURL"],device=device,user=user,
			siteDomain=self.settings["siteDomain"],action=action,messages=0)

class login(BaseHandler):
	@addslash
	def get(self):
		user = self.current_user
		if user :
			self.redirect("/")
		else:
			userAgent = self.request.headers["User-Agent"]
			device = 0 if "Mobile" in userAgent or "Android" in userAgent else 1

			self.render("login.html",siteName=self.settings["siteName"],
				siteURL=self.settings["siteURL"],device=device,user=user,
				siteDomain=self.settings["siteDomain"],action=None,messages=0)

	@gen.coroutine
	def post(self):
		db = self.settings["db"]
		password = hashlib.sha1(self.get_argument("password")).hexdigest()
		user = yield db.user.find_one({"user":self.get_argument("user"),
						"password":password})
		if user :
			self.set_secure_cookie("user",user["user"])
			self.redirect(self.request.headers["referer"])
		else:
			userAgent = self.request.headers["User-Agent"]
			device = 0 if "Mobile" in userAgent or "Android" in userAgent else 1
			action = "账号或密码错误！"
			self.render("login.html",siteName=self.settings["siteName"],
			siteURL=self.settings["siteURL"],device=device,user=user,
			siteDomain=self.settings["siteDomain"],action=action,messages=0)


class FollowCate(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		db = self.settings["db"]
		user = self.current_user
		cate_url = self.get_argument("cate")
		if user and cate_url:
			yield db.user.update({"user":user},
				{"$addToSet":{"FollowCate":cate_url}})

class QuitCate(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		db = self.settings["db"]
		user = self.current_user
		cate_url = self.get_argument("cate")
		if user and cate_url:
			yield db.user.update({"user":user},
				{"$pull":{"FollowCate":cate_url}})

class FollowUserAction(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		db = self.settings["db"]
		user = self.current_user
		FollowUser = self.get_argument("FollowUser")
		if user and FollowUser:
			message = {
				"type":1,
				"fromUser":user,
				"user":FollowUser,
				"time":datetime.datetime.now()}
			yield [db.user.update({"user":user},
				{"$addToSet":{"FollowUser":FollowUser}}),
			db.messages.insert(message)]

class QuitFollow(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		db = self.settings["db"]
		user = self.current_user
		FollowUser = self.get_argument("FollowUser")
		yield db.user.update({"user":user},{"$pull":{"FollowUser":FollowUser}})

class ClearMessage(BaseHandler):
	@authenticated
	@gen.coroutine
	def put(self):
		db = self.settings["db"]
		user = self.current_user
		yield db.messages.remove({"user":user},multi=True)

class logout(BaseHandler):
	@addslash
	def get(self):
		self.clear_cookie("user")
		self.redirect("/")
