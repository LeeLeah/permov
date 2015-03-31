# coding: UTF-8

from . import *
import base64
import json
from qiniu import Auth

class album(BaseHandler):

	@gen.coroutine
	def get(self):
		user = self.current_user
		db = self.settings["db"]
		siteName = self.settings["siteName"]
		siteURL = self.settings["siteURL"]
		siteDomain = self.settings["siteDomain"]
		device = self.get_device()
		try:
			page = int(self.get_argument("page"))
		except:
			page = 1
		cates,cateNum = yield [db.cate.find({"score":{"$gt":0},"img":{"$ne":""}},
			{"description":1,"name":1,"title":1,"url":1,"img":1}
			).skip((page-1)*12).limit(12).to_list(12),
			db.cate.count()]
		if cateNum % 12 == 0:
			pageNum = cateNum / 12
		else:
			pageNum = cateNum / 12 + 1
		if user:
			messages = yield self.getMessages(user)
		else:
			messages = 0

		self.render("album.html",user=user,siteName=siteName,
				staticURL=self.settings["staticURL"],
				messages=messages,page=page,pageNum=pageNum,
				siteURL=siteURL,siteDomain=siteDomain,cates=cates,device=device)


class index(BaseHandler):
	@gen.coroutine
	def get(self):
		user = self.current_user
		db = self.settings["db"]
		siteName = self.settings["siteName"]
		siteURL = self.settings["siteURL"]
		siteDomain = self.settings["siteDomain"]
		try:
			self.set_cookie("ref",self.get_argument("ref"))
		except:
			pass
		device = self.get_device()
		cates = yield db.cate.find({"score":{"$gt":0},"img":{"$ne":""}},
			{"description":1,"name":1,
			"title":1,"url":1,"img":1}).limit(12).to_list(12)
		if user:
			messages = yield self.getMessages(user)
		else:
			messages = 0

		self.render("index.html",user=user,siteName=siteName,
				staticURL=self.settings["staticURL"],messages=messages,
				siteURL=siteURL,siteDomain=siteDomain,cates=cates,device=device)



class qiniu(BaseHandler):
	@authenticated
	@gen.coroutine
	def get(self):
		ret = json.loads(base64.decodestring(self.get_argument("upload_ret")))
		db = self.settings["db"]
		check = yield db.img.find_one({"_id":ret["hash"]})
		if not check :
			data = {
					"_id": ret["hash"],
					"tags":[],
					"user": self.current_user,
					"cate": "其它",
					"cate_url":"33",
					"description":"",
					"time": datetime.datetime.now(),
					"up":0,"down":0,
					"views": 1}
			yield db.img.insert(data)

			self.redirect("/%s/edit/" % ret["hash"])

		else:
			self.redirect("/img/%s/" % check["_id"])


class upjson(BaseHandler):
	def get(self):
		q = Auth("**Qiniu_Token**", 
				"**Qiniu_Secret**")

		self.write({
			"qiniuToken":q.upload_token("gulipa",None,3600,
				{'returnBody':'''{"hash":$(etag)}''', 
				'returnUrl':self.settings["siteURL"] + "upload/"}),
			"imgUrl":"http://upload.qiniu.com/",
			"imageFieldName": "file",
			"imageAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
			"imageMaxSize": 2048000,
			"imageUrlPrefix": "",

			})
