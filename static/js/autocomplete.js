var autocomplete = {};
(function(autocomplete) {
    var from = {
            autocomplete: null,
            normalPlace: null,
            isTrig: false
        },
        to = {
            autocomplete: null,
            normalPlace: null,
            isTrig: false
        }

    var map,
        distanceMatrixService,
        directionsService, directionsDisplay,
        mapMarkers,
        setValue,
        streetFrom, streetTo;

    autocomplete.init = function(setValueParam, streetFromParam, streetToParam) {
        var options = {
            componentRestrictions: {
                country: 'ru'
            },
            locality: 'Voronezh',
            types: ['geocode']
        };
        setValue = setValueParam;
        streetFrom = streetFromParam;
        streetTo = streetToParam;

        from.autocomplete = new google.maps.places.Autocomplete((document.getElementById(streetFrom)), options);
        from.autocomplete.addListener('place_changed', onPlaceChangedFrom);

        to.autocomplete = new google.maps.places.Autocomplete((document.getElementById(streetTo)), options);
        to.autocomplete.addListener('place_changed', onPlaceChangedTo);

        distanceMatrixService = new google.maps.DistanceMatrixService;
    }

    autocomplete.initMap = function(mapId) {
        var uluru = {
            lat: 55.751244,
            lng: 37.618423
        };
        map = new google.maps.Map(document.getElementById(mapId), {
            zoom: 11,
            center: uluru,
            styles:[
                      {
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#f5f5f5"
                          }
                        ]
                      },
                      {
                        "elementType": "labels.icon",
                        "stylers": [
                          {
                            "visibility": "off"
                          }
                        ]
                      },
                      {
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#616161"
                          }
                        ]
                      },
                      {
                        "elementType": "labels.text.stroke",
                        "stylers": [
                          {
                            "color": "#f5f5f5"
                          }
                        ]
                      },
                      {
                        "featureType": "administrative.land_parcel",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#bdbdbd"
                          }
                        ]
                      },
                      {
                        "featureType": "administrative.locality",
                        "elementType": "labels",
                        "stylers": [
                          {
                            "visibility": "on"
                          }
                        ]
                      },
                      {
                        "featureType": "administrative.locality",
                        "elementType": "labels.icon",
                        "stylers": [
                          {
                            "visibility": "on"
                          }
                        ]
                      },
                      {
                        "featureType": "administrative.locality",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "visibility": "on"
                          }
                        ]
                      },
                      {
                        "featureType": "administrative.locality",
                        "elementType": "labels.text.stroke",
                        "stylers": [
                          {
                            "visibility": "on"
                          }
                        ]
                      },
                      {
                        "featureType": "poi",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#eeeeee"
                          }
                        ]
                      },
                      {
                        "featureType": "poi",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#757575"
                          }
                        ]
                      },
                      {
                        "featureType": "poi.park",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#e5e5e5"
                          }
                        ]
                      },
                      {
                        "featureType": "poi.park",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#9e9e9e"
                          }
                        ]
                      },
                      {
                        "featureType": "road",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#ffffff"
                          }
                        ]
                      },
                      {
                        "featureType": "road.arterial",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#757575"
                          }
                        ]
                      },
                      {
                        "featureType": "road.highway",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#dadada"
                          }
                        ]
                      },
                      {
                        "featureType": "road.highway",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#616161"
                          }
                        ]
                      },
                      {
                        "featureType": "road.local",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#9e9e9e"
                          }
                        ]
                      },
                      {
                        "featureType": "transit.line",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#e5e5e5"
                          }
                        ]
                      },
                      {
                        "featureType": "transit.station",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#eeeeee"
                          }
                        ]
                      },
                      {
                        "featureType": "water",
                        "elementType": "geometry",
                        "stylers": [
                          {
                            "color": "#c9c9c9"
                          }
                        ]
                      },
                      {
                        "featureType": "water",
                        "elementType": "labels.text.fill",
                        "stylers": [
                          {
                            "color": "#9e9e9e"
                          }
                        ]
                      }
            ]
        });

        mapMarkers = [];
        directionsService = new google.maps.DirectionsService;
        directionsDisplay = new google.maps.DirectionsRenderer();
        directionsDisplay.setMap(map);
    }

    function onPlaceChangedFrom() {
        from.normalPlace = getNormalPlace(from.autocomplete.getPlace());
        document.getElementById(streetFrom).value = from.normalPlace.strPlace;

        if (from.normalPlace.location)
            from.isTrig = true
        else
            from.isTrig = false

        if (from.isTrig && to.isTrig) {
            calculateAndDisplayPrice(from, to, setValue);
            calculateAndDisplayRoute(from.normalPlace.location, to.normalPlace.location, mapMarkers);
        }
    }

    function onPlaceChangedTo() {
        to.normalPlace = getNormalPlace(to.autocomplete.getPlace())
        document.getElementById(streetTo).value = to.normalPlace.strPlace;

        if (to.normalPlace.location)
            to.isTrig = true
        else
            to.isTrig = false

        if (from.isTrig && to.isTrig) {
            calculateAndDisplayPrice(from, to, setValue);
            calculateAndDisplayRoute(from.normalPlace.location, to.normalPlace.location, mapMarkers);
        }
    }

    function getNormalPlace(place) {
        var components = place.address_components;
        var result = {
                strPlace: "",
                location: {}
            },
            street, street_number, premise, city, region;

        for (var i = 0, component; component = components[i]; i++) {
            if (component.types[0] == 'route') {
                street = component['long_name'];
            }
            if (component.types[0] == 'street_number') {
                street_number = component['long_name'];
            }
            if (component.types[0] == 'premise') {
                premise = component['long_name'];
            }
            if (component.types[0] == 'locality') {
                city = component['long_name'];
            }
            if (component.types[0] == 'administrative_area_level_1') {
                region = component['long_name'];
            }

        }

        if (street) {
            result.strPlace = street;
            if (street_number) {
                result.strPlace += ', ' + street_number;
                if (premise) {
                    result.strPlace += ' (' + premise + ')';
                }
            }
        } else {
            if(city){
                result.strPlace = city + ', ' + region;
            }else{
                result.strPlace = region;
            }

        }

        result.location.lat = place.geometry.location.lat();
        result.location.lng = place.geometry.location.lng();

        return result;

    }

    function calculateAndDisplayPrice(from, to, setValue) {
        var origin = from.normalPlace.location;
        var destination = to.normalPlace.location;

        distanceMatrixService.getDistanceMatrix({
            origins: [origin],
            destinations: [destination],
            travelMode: 'DRIVING'
        }, function(response, status) {
            if (status == 'OK') {
                var distance = parseFloat(response.rows[0].elements[0].distance.text.replace(',', '.'));
                var cost = getPassageCost(distance);
                setValue(cost);
            }

        });

    }

    function getPassageCost(distance) {
        var hours = new Date().getHours(),
            price = (hours >= 22 || hours < 6) ? 30 : 25,
            cost = Math.round(price * distance);

        return cost;
    }

    function calculateAndDisplayRoute(pointA, pointB, markers) {

        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        markers.length = 0;


        var markerA = new google.maps.Marker({
                position: pointA,
                title: "point A",
                label: "A",
                map: map
            }),
            markerB = new google.maps.Marker({
                position: pointB,
                title: "point B",
                label: "B",
                map: map
            });
        markers.push(markerA);
        markers.push(markerB);

        directionsService.route({
            origin: pointA,
            destination: pointB,
            avoidTolls: true,
            avoidHighways: false,
            travelMode: google.maps.TravelMode.DRIVING
        }, function(response, status) {
            if (status == google.maps.DirectionsStatus.OK) {
                console.log(response)
                //directionsDisplay.setMap(map);
                directionsDisplay.setDirections(response);

            } else {
                window.alert('Directions request failed due to ' + status);
            }
        });
    }

})(autocomplete);
