function setDriverName(order, driver){
    $('[data-order-id="'+order.id+'"] [class="find_driver"]')
        .hide()
        .after('<p class="username"><a class="href" href="/profile_info/' + driver.id + '/">' + driver.first_name + '</a></p><a class="call-user" href="tel:+7' + driver.phone_number + '" >Позвонить</a>')
}

function cancelOrder(order){
    $('[data-order-id="'+order.id+'"] .call-user')
        .before('<p class="canceled-order">Заказ был отменен водителем</p>')
        .after('<a class="close-order" href="/close_order/'+order.id+'/">Закрыть</a>');
    $('.call-user').hide();
    $('.complete-order').hide();
    $('.cancel-order').hide();
    $('.more-info-order').hide();
}

function completeOrder(order){
    $('[data-order-id="'+order.id+'"]').remove();

    if($('[data-order-id]').size() == 0){
        $('.current-page').hide();
        $('<p class="empty-orders">Список ваших заказов пуст</p>').insertAfter('h1');
    }
}

var marker = new google.maps.Marker();

function sleep(millis) {
    var t = (new Date()).getTime(),
        i = 0;
    while (((new Date()).getTime() - t) < millis) {
        i++;
    }
}

function showCoordinates(order, coordinates){
    var map = window['map_'+order.id];
        map.setZoom(15);
        /*marker = new google.maps.Marker({
             position: coordinates[0],
             map: map
        });*/
        console.log(coordinates)
        marker.setPosition(coordinates[0]);
        marker.setMap(map);
   /* if(markers.length){
        for(var j=0; j<markers.length; j++){
            markers[j].setMap = null;
        }
        markers.length = 0;
    }*/

    //markers.push(marker);

        /*for (var i = 0; i < coordinates.length; i++) {
            marker = new google.maps.Marker({
                 position: coordinates[i],
                 map: map
            });
            map.setCenter(coordinates[i]);
            sleep(500);
            marker.setMap(null);
            marker = null;
        }*/
    function moveMarker(i){
        marker.setPosition(coordinates[i]);
        marker.setMap(map);
        map.panTo(coordinates[i]);
      //map.setCenter(coordinates[i]);
    }

    var i = 1;

    setTimeout(function run(){
        if(i >= coordinates.length){
            return
        }else{
            moveMarker(i);
            i += 1;
            setTimeout(run, 1000);
        }

    }, 1000);
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

            if(data.action == 'proccess'){
                setDriverName(data.order, data.driver);
            }else if(data.action == 'cancel'){
                cancelOrder(data.order);
            }else if(data.action == 'complete'){
                completeOrder(data.order);
            }else if(data.action == 'moveCoordinates'){
                showCoordinates(data.order, data.coordinates);
            }
    };
    // Лог ошибок
    ws_score.onerror = function (error) {
     console.log('WebSocket Error ' + error);
    };

} else {
	alert("Your browser doesn't support websockets\n Please try another browser.");
}
