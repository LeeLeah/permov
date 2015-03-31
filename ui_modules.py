# coding: UTF-8
import tornado.web

class AdminSideBar(tornado.web.UIModule):
	def render(self):
		return self.render_string("module/AdminSideBar.html")

class GulipaJC(tornado.web.UIModule):
	def render(self):
		user = self.current_user
		return self.render_string("module/GulipaJC.html",user=user)

class SideBarAd(tornado.web.UIModule):
	def render(self):
		userAgent = self.request.headers["User-Agent"]
		device = 0 if "Mobile" in userAgent or "Android" in userAgent else 1
		return self.render_string("module/SideBarAd.html",device=device)

class HeaderArea(tornado.web.UIModule):
	def render(self):
		user = self.current_user
		return self.render_string("module/HeaderArea.html",user=user)
