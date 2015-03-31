# coding: utf-8

from tornado import web,ioloop
import tornado.options
import tornado.httpserver
import routers
import os
import ui_module
import motor
import datetime

from tornado.options import define, options
define("port", default=80, help="run on the given port", type=int)

client = motor.MotorClient("mongodb://www.permov.com/")
client.admin.authenticate("***DB_Name***","***DB_Password***")
db = client.gulipa

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "*****YOUR_COOKIE_SECRET*****",
    "login_url": "/login/",
    "xsrf_cookies": True,
    "debug": True,
    "siteDomain": "www.permov.com",
    "siteURL": "http://www.permov.com/",
    "staticURL": "http://static.permov.com",
    "siteName": "喷沫屋",
    "ui_modules" : ui_module,
    "db": db,
    "gulipaTime":datetime.datetime(2015,2,14),
}


if __name__ == "__main__": 
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=routers.route,
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        **settings
        )
    http_server = tornado.httpserver.HTTPServer(app,xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
