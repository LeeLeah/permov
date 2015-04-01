from handlers import Index
from handlers import Img
from handlers import Search
from handlers import User
from handlers import SomePage
from handlers import Admin
from handlers import VIP

route = [
	(r"/",Index.index),
	(r"/([0-9]+)/?",Img.category),
	(r"/addLink/?",Img.addLink),
	(r"/addCate/?",VIP.addCate),
	(r"/Admin/addviptime/?",Admin.AddVipTime),
	(r"/Admin/suggest/?",Admin.AdminSuggest),
	(r"/addKeyword/?",Img.addKeyword),
	(r"/album/?",Index.album),
	(r"/clearMessage/?",User.ClearMessage),
	(r"/comment/?",Img.comment),
	(r"/delComment/?",User.delComment),
	(r"/FollowUser/?",User.FollowUserAction),
	(r"/FollowCate/?",User.FollowCate),
	(r"/img/([0-9a-zA-Z\_\-]+)/?",Img.img),
	(r"/nextimg/(.+)/?",Img.next),
	(r"/message/?",SomePage.Message),
	(r"/myAlbum/?",VIP.myAlbum),
	(r"/myAlbum/edit/([0-9]+)/?",VIP.editMyAlbum),
	(r"/search/?",Search.search),
	(r"/tag/(.+)/?",Search.tags),
	(r"/login/?",User.login),
	(r"/logout/?",User.logout),
	(r"/qq/?",User.QQ),
	(r"/QuitFollow/?",User.QuitFollow),
	(r"/QuitCate/?",User.QuitCate),
	(r"/reg/?",User.Reg),
	(r"/rule/?",SomePage.Rule),
	(r"/suggest/?",SomePage.Suggest),
	(r"/upload/?",Index.qiniu),
	(r"/upjson/?",Index.upjson),
	(r"/user/?",User.home),
	(r"/user/(.+)/?",User.UserPage),
	(r"/vip/?",SomePage.VIP),
	(r"/([0-9a-zA-Z\_\-]+)/edit/?",User.editImg),
	]
