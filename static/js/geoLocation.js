/**
 * Created by vage on 28.10.17.
 */
var geoLocation = {};
(function ( geoLocation, window, document, undefined ) {

    var geo_options = {
            enableHighAccuracy : true,
            maximumAge         : 0,
            timeout            : 10000
        },
        coordinates = [];
        geoLocation.id;

    geoLocation.init = function(){

    }

    function showMessage(text){
         alert(text);
    }

    geoLocation.checkPermission = function(){
        var geo_success = function (position) {
            navigator.geolocation.clearWatch(id);
            if(driverGeoActive){
                geoLocation.watch();
                console.log('watch ')
            }
        },
        geo_error = function (error) {
            if(error.code == 1){
                showMessage('Разрешите доступ к местоположению');
            }
            if(error.code == 2){
                showMessage('Сеть не активна');
            }
            if(error.code == 3){
                showMessage('Превышено время ожидания PERMISSION '+ error.message);
               // geoLocation.checkPermission();
            }
        }

        if ("geolocation" in navigator) {
          //  var id = navigator.geolocation.getCurrentPosition(geo_success, geo_error, geo_options);
            var id = navigator.geolocation.watchPosition(geo_success, geo_error, geo_options);

        } else {
            showMessage('Ваш браузер не поддерживает геолокацию');
        }

    }

    geoLocation.watch = function () {

        function geo_success (position) {
            var lsCoordinates = JSON.parse(localStorage.getItem('coordinates')),
                 coordinate = {
                    'lat': position.coords.latitude,
                    'lng': position.coords.longitude
                 };

            if (lsCoordinates){
                coordinates = lsCoordinates;
                console.log(lsCoordinates)
                localStorage.removeItem('coordinates');
            }

            if(coordinates.length == 10){
                coordinates.push(coordinate);
                sendCoordinates(coordinates);
                coordinates.length  = 0;
                console.log('coords sended')
            }else{
                coordinates.push(coordinate);
                console.log('coords added')
            }
           // alert(coordinate.lat);
        }

        function geo_error (error) {
            if(error.code == 1){
                showMessage('Разрешите доступ к местоположению');
            }
            if(error.code == 2){
                showMessage('Сеть не активна');
            }
            if(error.code == 3){
                showMessage('Превышено время ожидания');
            }
        }

       geoLocation.id = navigator.geolocation.watchPosition(geo_success, geo_error, geo_options);
    }

    function sendCoordinates(coordinates) {
        $.ajax({
            url: "{% url 'geo_send_position' %}",
            type: "POST",
            dataType: "json",
            data: { 'data': JSON.stringify( {
                'coordinates': coordinates,
                 csrfmiddlewaretoken: '{{ csrf_token }}'
                })
            },
            success: function(json) {
                if(json.isSend){
                    console.log('Position was sended');
                }
            },
            error: function(xhr,errmsg,err) {
                alert(err +" "+ errmsg)
            }
        });
    }

    $(window).on('beforeunload', function(){
        navigator.geolocation.clearWatch(geoLocation.id);
        if (coordinates.length){
            var coordinatesJSON = JSON.stringify(coordinates);
            localStorage.setItem('coordinates', coordinatesJSON);
            console.log('beforeunload');
            console.log(coordinates);
        }
    });

})( geoLocation, window, document );