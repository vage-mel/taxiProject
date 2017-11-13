function showNewOrder(order, user){

    if($('.empty-orders').size){
        $(".empty-orders").hide();
    }

    var divOrder = $('<div data-order-id="'+ order.id+'" class="order"></div>').insertAfter('h1');
    divOrder.append('<p class="username"><a href="/profile_info/'+user.id+'">'+user.firstName+'</a></p>' +
        '<p class="clock-icon" data-date="'+order.date+'">' + moment(order.date).fromNow() +'</p> ' +
        '<p class="from">'+ order.From +'</p>' +
        '<p class="to">'+ order.to +'</p>' +
        '<p class="money">'+ order.cost +' RUB </p>');

    if(order.infoOrder !=""){
         divOrder.append('<p class="note">{{ order.info_order }}</p>');
    }

    divOrder.append('<a class="perform-order" title="Выполнить" href="#" onclick="perfomOrder('+order.id+')">Выполнить</a>');
    /*sendNotification('Новый заказ',{
            body: 'Цена: ' + order.cost,
            dir: 'auto'
            });*/
}

function deleteOrder(order){
    $('[data-order-id="'+order.id+'"]').remove();
    if($('[data-order-id]').size() == 0){
        $('.current-page').hide();
        $('<p class="empty-orders">Список заказов пуст</p>').insertAfter('h1')
    }
}

if ("WebSocket" in window) {

    ws_public = new WebSocket("ws://" + ws_address + "/public/" + this.token + "/");
    ws_public.onopen = function() {
        console.log("public  websocket connection is opened...");
    };
    ws_public.onclose = function() {
        console.log("public websocket connection is closed...");
    };
    ws_public.onmessage = function(response) {
        var data = JSON.parse(response.data);

        if(data.action == 'create')
            showNewOrder(data.order, data.user);
        else if(data.action == 'delete')
            deleteOrder(data.order);
    };

} else {
	alert("Your browser doesn't support websockets\n Please try another browser.");
} 
