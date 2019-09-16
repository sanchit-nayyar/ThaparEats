update_form = function(){
	var body = document.body;
	var html = document.documentElement;
	var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
	$('#lgnfrm').css('margin-top', ((height - $('#lgnfrm').height()) / 2 - $('header').height()) + 'px');
}

update_form();
setInterval(update_form, 10);