$("#uploader").change(function(){
	var form = document.getElementById("picForm");
	QN = $.ajax({url:"/upjson/",async:false});
	var qiniu = eval("(" + QN.responseText + ")")
	var input = document.createElement("input");
		input.id = "token";
		input.name = "token";
		input.type = "hidden";
		input.value = qiniu.qiniuToken;
	form.appendChild(input);
	form.submit();
	$('#loadingModal').modal({
              backdrop:false
            })
})

function replyComment(id){
	var form = document.getElementById("imgCommentForm");
	var replyInput = document.getElementById("user-"+id);
	form.appendChild(replyInput);
	var placeholderText = document.getElementById("commentArea");
		placeholderText.placeholder = "回复：" + replyInput.value;
	$("#commentArea").focus().select();
}

function delComment(id){
	$.ajax({
			url:"/delComment/",
			type:"PUT",
			data:{"_xsrf":getCookie("_xsrf"),"commentId":id},
			success:function(){
				$("#close-"+id).hide()
				alert("删除成功！")
			}
		})
}

$("#QQLogin").click(function(){
	var A=window.location.href="https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101139552&redirect_uri=http://www.permov.com/qq/&state="+getCookie("_xsrf");
})

$("#search").change(function(){
	var form = document.getElementById("searchForm");
	form.submit();
})

$("#search").focus(function(){
	$("#searchBox").attr("class","col-md-12 col-xs-12 col-sm-12");
	$("#uploadButton").hide();
}).blur(function(){
	$("#searchBox").attr("class","col-md-8 col-xs-8 col-sm-8");
	$("#uploadButton").show();
})

$("#imgContent").click(function(){
	$("#tagsArea").toggle();
})

$("#imgArea").click(function(e){
	var form = document.getElementById("addLink");
	var leftInput = document.createElement("input");
		leftInput.id = "left";
		leftInput.name = "left";
		leftInput.type = "hidden";
		leftInput.value = getLeft(e);
	form.appendChild(leftInput);
	var topInput = document.createElement("input");
		topInput.id = "top";
		topInput.name = "top";
		topInput.type = "hidden";
		topInput.value = getTop(e);
	form.appendChild(topInput);
	var form = document.getElementById("addKeyword");
	var leftInput = document.createElement("input");
		leftInput.id = "left";
		leftInput.name = "left";
		leftInput.type = "hidden";
		leftInput.value = getLeft(e);
	form.appendChild(leftInput);
	var topInput = document.createElement("input");
		topInput.id = "top";
		topInput.name = "top";
		topInput.type = "hidden";
		topInput.value = getTop(e);
	form.appendChild(topInput);
})

function getLeft(e){
	e = e || window.event;
	var left = e.pageX || e.clientX + document.body.scroolLef;
	var imgAreaLeft = $("#imgArea").offset().left;
	var imgAreaWidth = $("#imgContent").width();
	var leftValue = (left - imgAreaLeft)/imgAreaWidth*100;
	if(leftValue>96){leftValue-=3}else{leftValue=leftValue}
	return leftValue
}

function getTop(e){
	e = e || window.event;
	var top = e.pageY || e.clientY + document.boyd.scrollTop;
	var imgAreaTop = $("#imgArea").offset().top;
	var imgAreaHeight = $("#imgContent").height();
	var topValue = (top - imgAreaTop)/imgAreaHeight*100;
	if(topValue>96){topValue -= 3}else{topValue=topValue}
	return topValue
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

$("#clearMessage").click(function(){
	$.ajax({
			url:"/clearMessage/",
			type:"PUT",
			data:{"_xsrf":getCookie("_xsrf")},
			success:function(){
				alert("您已成功清空所有消息！")
				location.reload();
			}
		})
})

function FollowUser(id){
		$.ajax({
			url:"/FollowUser/",
			type:"PUT",
			data:{"FollowUser":id,"_xsrf":getCookie("_xsrf")},
			success:function(){
				var FollowUser = document.getElementById(id);
				FollowUser.className = "btn btn-default btn-block";
				FollowUser.value = "取消";
				FollowUser.onclick = function (){ 
              		QuitFollow(this.id)};
			}
		})
	};

function QuitFollow(id){
	$.ajax({
			url:"/QuitFollow/",
			type:"PUT",
			data:{"FollowUser":id,"_xsrf":getCookie("_xsrf")},
			success:function(){
				var QuitFollow = document.getElementById(id);
				QuitFollow.className = "btn btn-success btn-block";
				QuitFollow.value = "关注";
				QuitFollow.onclick = function (){ 
              		FollowUser(this.id)};
			}
		});
	};
function FollowCate(id){
		$.ajax({
			url:"/FollowCate/",
			type:"PUT",
			data:{"_xsrf":getCookie("_xsrf"),"cate":id },
			success:function(){
				var FollowCity = document.getElementById(id);
				FollowCity.className = "btn btn-default btn-block";
				FollowCity.value = "取消";
				FollowCity.onclick = function (){ 
              		QuitCate(this.id)};
			}
		})
	};
function QuitCate(id){
	$.ajax({
			url:"/QuitCate/",
			type:"PUT",
			data:{"_xsrf":getCookie("_xsrf"),"cate":id },
			success:function(){
				var QuitCity = document.getElementById(id);
				QuitCity.className = "btn btn-success btn-block";
				QuitCity.value = "关注";
				QuitCity.onclick = function (){ 
              		FollowCate(this.id)};
			}
		})
};
function getCookie(c_name){
if (document.cookie.length>0)
  {
  c_start=document.cookie.indexOf(c_name + "=")
  if (c_start!=-1)
    { 
    c_start=c_start + c_name.length+1 
    c_end=document.cookie.indexOf(";",c_start)
    if (c_end==-1) c_end=document.cookie.length
    return unescape(document.cookie.substring(c_start,c_end))
    } 
  }
return ""
}