function cancelOrder(order){
    $('[data-order-id="'+order.id+'"] .call-user')
        .before('<p class="canceled-order">Заказ был отменен пользователем</p>')
        .after('<a class="close-order" href="/close_order/'+order.id+'/">Закрыть</a>');
    $('.call-user').hide();
    $('.complete-order').hide();
    $('.cancel-order').hide();
}

if ("WebSocket" in window) {

    ws_score = new WebSocket("ws://" + ws_address + "/private/" + this.token + "/");
    ws_score.onopen = function() {
        console.log("private connection is opened...");
    };
    ws_score.onclose = function() {
        console.log("private connection is closed...");
    };
    ws_score.onmessage = function(response) {
        var data = JSON.parse(response.data);

        if(data.action == 'cancel')
            cancelOrder(data.order);

    };
    // Лог ошибок
    ws_score.onerror = function (error) {
     console.log('WebSocket Error ' + error);
    };

} else {
	alert("Your browser doesn't support websockets\n Please try another browser.");
}
