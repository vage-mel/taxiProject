/* Slidemenu */

(function() {
	var $body = document.body,
		$menu_trigger = $body.getElementsByClassName('menu-trigger')[0];
	$body.className = 'menu-active';

	if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
		$body.className = '';
	}
	if (typeof $menu_trigger !== 'undefined') {
		$menu_trigger.addEventListener('click', function() {
			$body.className = ($body.className == 'menu-active') ? '' : 'menu-active';
		});
	}

}).call(this);