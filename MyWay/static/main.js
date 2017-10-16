$(document).ready(function() {
	$('.delete').click(function(event) {
		if (!confirm('確定刪除嗎?')) {
			event.preventDefault();
		} else {
			window.location.replace($(this).attr('href'));
		} 
	});
});