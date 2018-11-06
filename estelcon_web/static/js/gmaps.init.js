$(function () {

    map();

});

/* map */

function map() {

    var styles = [{"featureType": "landscape", "stylers": [ {"visibility": "on"}]}, 
                    {"featureType": "poi", "stylers": [ {"visibility": "simplified"}]}, 
                    {"featureType": "road.highway", "stylers": [ {"visibility": "simplified"}]}, 
                    {"featureType": "road.arterial", "stylers": [{"lightness": 50}, {"visibility": "on"}]}, 
                    {"featureType": "road.local", "stylers": [{"lightness": 50}, {"visibility": "on"}]}, 
                    {"featureType": "transit", "stylers": [{"visibility": "simplified"}]}, 
                    {"featureType": "administrative.province", "stylers": [{"visibility": "off"}]}, 
                    {"featureType": "water", "elementType": "labels", "stylers": [{"visibility": "on"}]}, 
                    {"featureType": "water", "elementType": "geometry", "stylers": []}];
    map = new GMaps({
        el: '#map',
        lat: 39.728558, 
        lng: -1.107522,
        zoomControl: true,
        zoomControlOpt: {
            style: 'SMALL',
            position: 'TOP_LEFT'
        },
        panControl: false,
        streetViewControl: false,
        mapTypeControl: false,
        overviewMapControl: false,
        scrollwheel: false,
        draggable: false,
        styles: styles
    });

    var image = 'img/marker.png';

    map.addMarker({
        lat: -12.043333,
        lng: -77.028333,
        icon: image/* ,
         title: '',
         infoWindow: {
         content: '<p>HTML Content</p>'
         }*/
    });
}
