update_prompt = function(){
	var body = document.body;
	var html = document.documentElement;
	var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
	$('.messagePrompt').css('top', ((height - $('.messagePrompt').height()) / 2) + 'px');
}

update_prompt();
setInterval(update_prompt, 10);

$('.closeImg').click(function(){
	$('.messagePrompt').hide();
})