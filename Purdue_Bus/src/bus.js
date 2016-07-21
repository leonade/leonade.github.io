// created by Li on 2015-9-17 22:31:02

/* Map related functions*/
function map_initialize() {
  var currentLatlng = new google.maps.LatLng(40.4196825873663, -86.8959383306467);
  var myOptions = {
    zoom: 14,
    center: currentLatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  addUserLocation()
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(function(p){
      newLatlng = new google.maps.LatLng(p.coords.latitude, p.coords.longitude)
      if(google.maps.geometry.spherical.computeDistanceBetween(newLatlng, currentLatlng)<10000){
        currentLatlng = newLatlng
      // p1 = currentLatlng
        map.setCenter(currentLatlng);
        map.setZoom(16);
        nearest_stop = ''
        nearest_dist = 40000000
        for (stop in stops){
          //console.log(stop)
          this_LatLng = new google.maps.LatLng(stops[stop].Lat,stops[stop].Lon)
          this_distance = google.maps.geometry.spherical.computeDistanceBetween(currentLatlng, this_LatLng);
          if(this_distance < nearest_dist){
            nearest_dist = this_distance;
            nearest_stop = stop;
          }
        }
      }
      setTimeout('activate_stop(stop)',10000)
    })
  }
}

function activate_stop(stop){
  routes_to_be_activated = []
  current_routes.forEach(function(route){
	if (route.stops.indexOf(nearest_stop)>-1){
	  routes_to_be_activated.push(route.ID)
	  console.log(route.ID, route.name, 'activated')
	}
  })
  $.unique(routes_to_be_activated).forEach(function(route_ID){
	$(".route").each(function(i, route_div){
	  if(route_ID == route_div.id){
		activate_route(route_div)
	  }
	})
  })
  var contentString = '<div id="content">'
}

// user location arrow
// http://stackoverflow.com/questions/28396206/google-maps-js-api-v3-show-orientation-arrow-on-my-location-marker
function addUserLocation() {
  myLocationMarker = new google.maps.Marker({
    clickable : false,
    icon: {
        path: 'M 5.0517245, 32.674 C 4.9472404, 32.6618415 3.7952519, 36.2516765 2.4220369, 42.2911935 1.1587964, 47.8470325 0.12521192, 52.425275 0.12516192, 52.46463 c 0, 0.039355 0.0078845, 0.061575 0.0171875, 0.05 0.152837, -0.19015 4.17575798, -5.01912 4.2375, -5.159374 0.2265875, -0.228013 0.5227495, -4.3669825 0.6718751, -8.2375 0.149125, 3.870534 0.446849, 8.0094855 0.6734375, 8.2375 0.061742, 0.140254 4.084663, 4.969224 4.2375, 5.159374 0.009303, 0.011575 0.017255, -0.010645 0.0171875, -0.05 0, -0.039355 -1.0336345, -4.6175975 -2.296875, -10.1734365 -1.373215, -6.039517 -2.5252035, -9.629352 -2.6296875, -9.6171875 -0.00025, 0.00149 -0.00133, 0.00319 -0.00156, 0.004685 -0.0002, -0.00143 0.0002, -0.00327 0, -0.004685 z',
        strokeColor : '#1a9ae0',
        strokeWeight : 0,
		fillColor: '#1a9ae0',
        fillOpacity: .9,
        anchor: new google.maps.Point(5,45),
        scale: 1
      },
    shadow : null,
    zIndex : 999,
    map : map
  });

  enableWatchPosition();
  enableOrientationArrow();
}

function enableWatchPosition() {
  if (navigator.geolocation) {
    watchPositionId = navigator.geolocation.watchPosition(locateByBrowser, handleErrorGettingLocation, {
      timeout : 30000,
      enableHighAccuracy : true,
      maximumAge : 1000
    });
  }
}

function handleErrorGettingLocation (e){
  console.log('Error in getting location.')
}

function locateByBrowser(location) {

  var currentLocation = new google.maps.LatLng(location.coords.latitude, location.coords.longitude);
  myLocationMarker.setPosition(currentLocation);
}

function enableOrientationArrow() {

  if (window.DeviceOrientationEvent) {

    window.addEventListener('deviceorientation', function(event) {
      var alpha = null;
      //Check for iOS property
      if (event.webkitCompassHeading) {
        alpha = 360-event.webkitCompassHeading;	//https://mobiforge.com/design-development/html5-mobile-web-device-orientation-events
      }
      //non iOS
      else {
        alpha = event.alpha;
      }
      var locationIcon = myLocationMarker.get('icon');
      locationIcon.rotation = 360 - alpha;
      myLocationMarker.set('icon', locationIcon);
    }, false);
  }
}

function size_of_zoom(){
  var size
  var zoom =  map.getZoom();
  if (zoom >= 19) { 
    size = 40
  } 
  else if (zoom <= 15) {
    size = 16
  }
  else{
    size = int(40/Math.pow(1.3,19-zoom))
  }
  return(size)
}

function icon_initialize(){
  //var image = 'icon/'+route['ID']+'.png';
  //var size = 30
  var size = size_of_zoom()
  car_icons = {}
  
  var image = {
    url: 'icon/stop_icon.svg',
    // This marker is 20 pixels wide by 32 pixels high.
    scaledSize : new google.maps.Size(size/2,size/4),
    // The origin for this image is (0, 0).
    origin: new google.maps.Point(0,0),
    // The anchor for this image is the base of the flagpole at (0, 32).
    anchor: new google.maps.Point(size/4,size/8)
  }
  stop_icon = image
  
  routes.forEach(function(route){
    var image = {
      url: 'icon/'+route['ID']+'.png',
      // This marker is 20 pixels wide by 32 pixels high.
      scaledSize : new google.maps.Size(size, size),
      // The origin for this image is (0, 0).
      origin: new google.maps.Point(0, 0),
      // The anchor for this image is the base of the flagpole at (0, 32).
      anchor: new google.maps.Point(size/2, size/2)
    }
    car_icons[route['ID']] = image
  })
  
  google.maps.event.addListener(map,'zoom_changed', function() {
    var zoom =  map.getZoom();
    var size = size_of_zoom()
    for (key in car_icons){
      car_icons[key].scaledSize = new google.maps.Size(size,size)
      car_icons[key].anchor = new google.maps.Point(size/2, size/2)
    }
    //stop_icon.scaledSize = new google.maps.Size(size,size/2)
    //stop_icon.anchor = new google.maps.Point(size/2, size/4)
    if(zoom<14){
      for (stop in stops){
        stops[stop].marker.setVisible(false)
        //stops[stop].marker.setIcon(stop_icon)
      }
	}
  })
}

function encode_route(route){
  var path = google.maps.geometry.encoding.encodePath(route.path.getPath()).replace('\\','\\\\')
  //console.log(path)
  return(path)
}

debug_draw_route = false;

function draw_stop_debug(i, stop){
  if (stop === undefined){    //debugging
    stop = i
    i = 'HereH'
  }
  var stopMarker = new google.maps.Marker({
    draggable: false,
    position: {lat: parseFloat(stops[stop]['Lat']), lng: parseFloat(stops[stop]['Lon'])},
    //label: route['duration'][i].toString(),
    label: i.toString().split("").reverse().join(""),
    stop_id: stop,      
    //icon: stop_icon,
    visible: debug_draw_route,
    map: map
  });
  stopMarker.addListener('click', function() {
    console.log(stopMarker.stop_id, stopMarker.label)
  });
}

function draw_route(route){
  var decodedPath = google.maps.geometry.encoding.decodePath(route['polyline']);
  var decodedLevels = decodeLevels(Array(decodedPath.length).join("B"));
  //opacity = typeof opacity !== 'undefined' ? opacity : 42
  
  //if(route.path!==undefined){route.path.setVisible(false)}
  route.path = new google.maps.Polyline({
    path: decodedPath,
    levels: decodedLevels,
    strokeColor: color[route["ID"]],
    strokeOpacity: 1, //0.1
    originalOpacity: 1, //0.1
    strokeWeight: 4,
    map: map,
    route: route    // for click event
  });
  if(route.status == 'Running' && !debug_draw_route){
    set_route_opacity(route,0.4)
    route.path.originalOpacity = 0.4
  }
  if(route.status == 'Not Running' && !debug_draw_route){
    set_route_opacity(route,0.1)
    route.path.originalOpacity = 0.1
  }
  if(route.status == 'No Service' && !debug_draw_route){
    set_route_opacity(route,0)
    route.path.originalOpacity = 0
  }
  route.path.addListener('click', function() {
    console.log(route.path.route.ID, route.path.route.name)
    routes.forEach(function(route){
      route.click_activated = false
      if(!route.web_activated){
        set_route_opacity(route,route.path.originalOpacity)
      }
    })
    route.path.route.click_activated = true
    set_route_opacity(route,0.9)
	route.path.setOptions({'zIndex':MaxZIndex})
	MaxZIndex++
    find_car(route)
	show_stops(route)
	//bound_path(route.path)
  });
  //route.path.edit();
  //console.log(route.ID,route.name,route.stops[0],route.stops[route.stops.length-1]);
  //console.log(route.distance);
  if (debug_draw_route){
    $.each(route.stops, function(i, stop){
      //return
      draw_stop_debug(i, stop)
    })
  }
  //var bounds = new google.maps.LatLngBounds();
  //loc = new google.maps.LatLng("45.478294","9.123949");
  //bounds.extend(loc);
}

function bound_path(path){
  var bounds = new google.maps.LatLngBounds();
  path.getPath().getArray().forEach(function(x){
    bounds.extend(x)
	//google.maps.event.trigger(markers[i], 'click');
  })
  map.fitBounds(bounds);
}

function set_route_opacity(route,opacity){
  route.path.setOptions({strokeOpacity:opacity})
}
function show_stops(route){
  for (stop in stops){
    stops[stop].marker.setVisible(false)
  }
  route.stops.forEach(function(stop){
    var icon = stops[stop].marker.getIcon()
	icon.strokeColor = color[route.ID]
    stops[stop].marker.setIcon(icon)
    stops[stop].marker.setVisible(true)
  })
}

function to_time_string(secs){
  if(secs>=60){return( Math.floor(secs/60) + ' min ' + secs%60 + ' secs')}
  else{return( secs%60 + ' secs')}
}
info = undefined
function draw_stop(stop){
  var stopMarker = new google.maps.Marker({
    draggable: false,
    position: {lat: parseFloat(stops[stop]['Lat']), lng: parseFloat(stops[stop]['Lon'])},
    //label: route['duration'][i].toString(),
    stop_id: stop,  
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      strokeColor : '#1a9ae0',
      strokeWeight : 5,
      strokeOpacity : 0.9,
      fillColor: '#1a9ae0',
      fillOpacity: 0,
      //anchor: new google.maps.Point(5,45),
      scale: 2
    },
    visible: false,
    map: map
  });
  stopMarker.addListener('click', function() {
    if(info !== undefined){info.close()}
    var stop = stopMarker.stop_id;
	content = '<b>' + stop + '</b> :' + stops[stop].StopDesc + '<br\>'
	var arrivals = []
	stops[stop].arrival_times.arrival.forEach(function(arrival){
	  var name = arrival[0]
	  arrivals.push([name.slice(0,name.indexOf(' ')),arrival[1]])
	})
	added_ID = ''
	routes.forEach(function(route){
	  var added = false
	  if(added_ID != route.ID){
	    arrivals.forEach(function(arrival){
	      if(arrival[0] == route.ID){
		    if(!added){
		      content += "<img class='routeImage' width=\"20\" height=\"20\" style=\"vertical-align:middle\" src=\"icon\\"+route.ID+'.png\">'
		      added = true
			  added_ID = route.ID
		    }
		      content += '&nbsp;&nbsp;' + to_time_string(arrival[1])
	      }
	    })
	  }
	  if(added){
	    content += '<br/>'
	  }
	})
    info = new google.maps.InfoWindow({
      content: content
    });
	info.open(map, stopMarker);
    console.log(stopMarker.stop_id)
  });
  stops[stop].marker = stopMarker
}

//cars_marker = []
function draw_car(car){
  //cars[route['name']].forEach(function(car){
    //if(car.marker == undefined){    // new route
      GPosition = car.route.path.GetPointAtDistance(car['loc'])
      var carMarker = new google.maps.Marker({
        map: map,
        position: GPosition, //{lat: GPosition.G, lng: GPosition.K},
        icon: car_icons[car.route['ID']],
        //animation: google.maps.Animation.DROP,
        draggable: false,
        visible: false,
        zIndex : 998
      });
      car['marker'] = carMarker
    //}
  //})
}

function update(){
  time_stamp = new Date().getTime()
  routes.forEach(function(route){
    route.activated = route.click_activated || route.web_activated
    // update running info ('Running'/'Not Running') every 10 min
    if (time_stamp-route.time_stamp > 600000){
      running_info_initialize();
      draw_current_routes()
      current_routes.forEach(find_car);
    }
  })
  // remove arrived cars, set upcoming cars visible
  for (var key in cars){
    $.each(cars[key],function(car_index,car){
      if(car.loc >= car.route.path.Distance()){
        console.log(car.route.ID,car.route.name,'deleted')
        car.marker.visible=false
        delete car.marker
        delete cars[key][car_index]
      }else if(car.loc > car.next_dist){
        console.log(car.route.ID,car.route.name,'arrived at stop')
        car.speed = 0
		car.loc = car.next_dist
      }else if(car.running_time >= -1200 && car.route.activated){    // set upcoming cars in 20 min visible
        car.marker.setVisible(true)
      }else if (time_stamp-car.time_stamp > 60000 && car.route.activated){    // update cars location every 1 min
        find_car(car.route);
      }else{
        car.marker.setVisible(false)
      }
    })
    cars[key] = cars[key].filter(function(item){return(item!==undefined)})
  }
}

tick = 100
function animate() {
  // alert("animate("+d+")");
  update()
  for (var key in cars){
    $.each(cars[key],function(i,car){
      var p
      car.loc += car.speed*tick/1000
      car.running_time += tick/1000
      p = car.route.path.GetPointAtDistance(car.loc);
      //map.panTo(p);
      car.marker.setPosition(p);
      car.marker.setIcon(car_icons[car.route['ID']]);
    })
  }
  timerHandle = setTimeout(animate, tick);
}

          
//carMarker.setIcon(image)


function decodeLevels(encodedLevelsString) {
  var decodedLevels = [];

  for (var i = 0; i < encodedLevelsString.length; ++i) {
    var level = encodedLevelsString.charCodeAt(i) - 63;
    decodedLevels.push(level);
  }
  return decodedLevels;
}

/* Time related & customized functions*/
dt = new Date();
//var dt = new Date(2015, 5, 1, 12, 0, 59, 0);
Day = dt.getDay()
//alert(dt2.getFullYear() + ":" + dt2.getMonth() + ":" + dt2.getDate() + ":" + dt2.getDay())
//alert(earlier_than('03:00'))
var over_night = current_earlier_than('03:00')
if(over_night){
  Day = (Day+6)%7
  //alert(Day)
}
function int(num){return(parseInt(num,10))}
function sum(A){return(A.reduce(function(a,b){return(a+b)}))}
function earlier_than(time_str1,time_str2){
  time1 = time_str1.split(':');
  hour1 = int(time1[0]);
  min1 = int(time1[1]);
  time2 = time_str2.split(':');
  hour2 = int(time2[0]);
  min2 = int(time2[1]);
  if(hour1 < hour2){return(true)}
  else if(hour1 > hour2){return(false)}
  else{
    if(min1 < min2){return(true)}
    else if(min1 >= min2){return(false)}
  }
}
//alert('here')
function current_earlier_than(time_str){
  return(earlier_than(dt.getHours()+':'+dt.getMinutes(), time_str))
}

function running_info_initialize(){
  current_routes = [];

  //alert(time + dt.getDay())
  function running(route){
    var operation_day
    var operation_time
    if (Day == 0){
      operation_day = 'Sunday'
      operation_time = route.operation_time.Sun
      if (route.ID == '21'){    // special treatment on Route 21: special hours on Thu-Fri stored in Sun
        operation_time = ["00:00", "00:00"]
      }
    }
    else if (Day == 6){
      operation_day = 'Saturday'
      operation_time = route.operation_time.Sat
    }
    else {
      operation_day = 'Weekday'
      operation_time = route.operation_time.Weekday
      if ((route.ID == '21') && (Day==4 || Day==5)){    // special treatment on Route 21: special hours on Thu-Fri
        operation_time = route.operation_time.Sun
      }
    }
    //operation_info = operation_day+': '+operation_time[0]+' - '+operation_time[1];
    operation_info = operation_time[0]+' - '+operation_time[1];
    // Compare with operation time
    //alert(operation_time)
    // ['0:0','0:0']
    if (operation_time[0] == '00:00'){ return (['No Service', 'on '+operation_day])}
    // late night buses
    else if (earlier_than(operation_time[1], '03:00')){
      if(over_night){
        if (current_earlier_than(operation_time[1])){ return (['Running', operation_info])}
        else { return (['Not Running', operation_info])}
      }
      else{
        if (current_earlier_than(operation_time[0])) { return (['Not Running', operation_info])}
        else { return (['Running', operation_info])}
        }
    }
    // common buses
    else {
      if(over_night){
        return (['Not Running', operation_info])
      }
      else{
        if (!(current_earlier_than(operation_time[0])) && current_earlier_than(operation_time[1])) 
          {return (['Running', operation_info])}
        else { return (['Not Running', operation_info])}
      }
    }
  }

  $.each(routes, function(i, route){
    //route_div.innerHTML += "<div class='researcher_name'>" + researcher.researcher_name + "</div>"
    //running(route) 
    running_info = running(route)
    route.status = running_info[0]
    route.operation_info = running_info[1];
    if(route.status == 'Running'){
      current_routes.push(route);
    }
  });
  
  //return (routes)
}

function draw_current_routes(){
  $.each(routes, function(i, route){
    if(route.path === undefined && !debug_draw_route){
      draw_route(route)
    }
  });
}

function convertHex(hex,opacity){
    hex = hex.replace('#','');
    r = parseInt(hex.substring(0,2), 16);
    g = parseInt(hex.substring(2,4), 16);
    b = parseInt(hex.substring(4,6), 16);

    result = 'rgba('+r+','+g+','+b+','+opacity+')';
    return result;
}
function route_gradient(route,highlight){
  if(highlight){
    return('linear-gradient(' + convertHex(color[route.ID],0.75) + ',' + convertHex(color[route.ID],0.85) + ')')
  }else if(route.status == 'Running'){
    return('linear-gradient(' + convertHex(color[route.ID],0.55) + ',' + convertHex(color[route.ID],0.65) + ')')
  }else if(route.status == 'Not Running'){
    return('linear-gradient(' + convertHex(color[route.ID],0.25) + ',' + convertHex(color[route.ID],0.35) + ')')
  }else{
    return('linear-gradient(' + convertHex("#000000",0.35) + ',' + convertHex('#000000',0.45) + ')')
  }
}
function layout_route_info(route){
  var route_div=document.createElement("div");
  route_div.id = route.ID;
  route_div.className = "route";
  route_div.style.background = route_gradient(route,false);
  route_div.addEventListener("click", function(){activate_route(route_div)});
  route_div.innerHTML += "<img class='routeImage' width=\"20\" height=\"20\" style=\"vertical-align:middle\" src=\"icon\\"+route.ID+'.png\">'
  route_div.innerHTML += "<span class='name'>&nbsp;&nbsp;" + route.name.replace(' Inbound','').replace(' Outbound','').replace(' Saturday','').replace(' Weekday','').replace(' Sunday','').replace(' Evening','').replace(' Express AM','').replace(' Express PM','').replace(' North and South','') +  "</span><br/>"
  if(route.status == 'No Service'){
    route_div.innerHTML += "<span class='ID'>No Service&nbsp;" + route.operation_info + "</span><br/>"
  }else{
    route_div.innerHTML += "<span class='ID'>" + route.status + '&nbsp;' + route.operation_info + "</span><br/>"
  }
  return(route_div)
}
function route_info(){
  //temp_routes = routes.slice()
  $("#info_canvas").empty()
  shown_ID = []
  routes.filter(function(route){return(route.status=='Running')}).forEach(function(route){
    if (shown_ID.indexOf(route.ID)<0){
	  //route_div = layout_route_info(route)
	  //activate_route(route_div)
      $("#info_canvas").append(layout_route_info(route));
      shown_ID.push(route.ID)
    }
  })
  routes.filter(function(route){return(route.status=='Not Running')}).forEach(function(route){
    if (shown_ID.indexOf(route.ID)<0){
      $("#info_canvas").append(layout_route_info(route));
      shown_ID.push(route.ID)
    }
  })
  routes.filter(function(route){return(route.status=='No Service')}).forEach(function(route){
    if (shown_ID.indexOf(route.ID)<0){
      $("#info_canvas").append(layout_route_info(route));
      shown_ID.push(route.ID)
    }
  })
}

MaxZIndex = 1
function activate_route(route_div){
  console.log(route_div.id)
  routes.forEach(function(route){
    if(route.ID == route_div.id){
      route.web_activated = !route.web_activated
      if(route.web_activated){
	    //draw_route(route);
		route.path.setOptions({'zIndex':MaxZIndex})
		MaxZIndex++
        find_car(route);
        route_div.style.background = route_gradient(route,true);
        route_div.style.color = '#eee';
        set_route_opacity(route,0.8)
		bound_path(route.path)
      }else{
		route.path.setOptions({'zIndex':0})
        route_div.style.background = route_gradient(route,false);
        route_div.style.color = '#555';
        set_route_opacity(route,route.path.originalOpacity)
      }
    }
  })
}

yql_count = 0
yql_queue = {}
function get_arrival_time(this_stop){
  if(!(this_stop in yql_queue)){
   if(!('arrival_times' in stops[this_stop]) || (new Date().getTime()-stops[this_stop]["arrival_times"].time_stamp > 1000)){
    //console.log(this_stop);
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D'http%3A%2F%2Fmyride.gocitybus.com%2Fpublic%2Flaf%2Fweb%2FViewStopNew.aspx%3Fsp%3D"+stops[this_stop]['url']+"%26pt%3D30%26r%3D60'%20and%20xpath%3D'%2F%2F*%5B%40id%3D%22_ctl0_cphMainContent_lookupResults_gvDepartureTimes%22%5D%2Ftbody'&format=json&diagnostics=true&callback="
    query = $.getJSON(url,{},function(response){
      // x=response;
      var time_stamp = new Date().getTime()
      var arrival_times = {time_stamp:time_stamp, arrival:[]}
      $.each(response['query']['results']['tbody']['tr'], function(i,tr){
        if (i >= 1) {
          var r = tr['td'][1]['font']['span']['content']
          var t = tr['td'][3]['font']['span']['content']
          if (t == 'DUE') { t = 0}
          else {t = int(t)*60}
          arrival_times.arrival.push([r,t])
        }
      })
      //console.log(this_stop)
      stops[this_stop]["arrival_times"] = arrival_times;
      yql_count++;
      delete yql_queue[this_stop]
    })
    yql_queue[this_stop] = query
    return(query)
   }
  }else{
    return(yql_queue[this_stop])
  }
}

function get_cars_location(route){
  //console.log(this_stop);
  var time_stamp = new Date().getTime()
  var stop_list = route['stops'].slice(0,route['stops'].length-1)
  var arrival_times = []    // arrival times for this route at each stop
  $.each(stop_list, function(i,stop){
    arrival_times.push((stops[stop]['arrival_times']['arrival'].filter(function(arrival){return(arrival[0].indexOf(route['ID']) == 0)}).map(function(arrival){return(arrival[1])})))
  })
  var cars_loc_s = []  // running cars location (seconds from final stop) for this route
  arrival_times[0].forEach(function(at){cars_loc_s.push({arrival_stop:0,time:[at]})})
  for(stop_index = 1; stop_index < arrival_times.length; stop_index++){
    //console.log(stop_index)
    if (arrival_times[stop_index].length >0){
      cars_loc_s.map(function(car){
        car.time = car.time.map(function(at){
          return(at+route['duration'][stop_index])
        })
      })  // get the arrival time at next stop
    }
    for(arrival_index=0; arrival_index < arrival_times[stop_index].length; arrival_index++){
      var match = false
      var at = arrival_times[stop_index][arrival_index]
      var car_index = 0
      while(!match && car_index < cars_loc_s.length){
        cars_loc_s[car_index].time.some(function(car_time){
          if(Math.abs(car_time - at)<=240){
            match = true
            cars_loc_s[car_index].time.push(at)
            return(true)
          }
        })
        car_index++
      }
      if(!match){
        cars_loc_s.push({arrival_stop:stop_index,time:[at]})
      }
    }
  }
  var cars_loc_m = []
  cars_loc_s.map(function(car){
    //if(car.arrival_stop==0){return}  // filter not departured cars
    if(car.time.length<arrival_times.slice(car.arrival_stop).filter(function(ar){return(ar.length)}).length-1){return}  // filter cross-stops on double way
    dist = 0
    speed = 0
    running_time = sum(route.duration) - sum(car.time)/car.time.length
    route['distance'].slice(0,car.arrival_stop).map(function(d){dist+=d})
	next_dist = dist+route['distance'][car.arrival_stop]
    if(arrival_times[car.arrival_stop][0]==0){  // DUE on arrival_stop
      dist += route['distance'][car.arrival_stop]
      speed = 0
    }else{
      if(arrival_times[car.arrival_stop][0] <= route['duration'][car.arrival_stop]){
        dist += route['distance'][car.arrival_stop] * (1-arrival_times[car.arrival_stop][0]/route['duration'][car.arrival_stop])
        speed = route['distance'][car.arrival_stop] / arrival_times[car.arrival_stop][0]
      }else{
        dist += route['distance'][car.arrival_stop] * (1-1)
        speed = route['distance'][car.arrival_stop] / arrival_times[car.arrival_stop][0]
      }
    }
    cars_loc_m.push({route:route,loc:dist,speed:speed,next_dist:next_dist,running_time:running_time,time_stamp:time_stamp})
  })
  return(cars_loc_m)
}

function find_car(route){
  //console.log(route['name']);
  //$.each(route['stops'],function(i, this_stop)  {get_arrival_time(this_stop)})
  //if(route['name']=='Salisbury Evening Saturday Inbound'){
  x = route
  var promises = []
  $.each(route['stops'], function(i,this_stop) { promises.push(get_arrival_time(this_stop))})
  $.when.apply($, promises).then(function() {
    new_cars = get_cars_location(route)
    if(cars[route['name']]=== undefined){
      cars[route['name']] = new_cars
      new_cars.forEach(draw_car)
    }else{
      new_cars.forEach(function(new_car){// push car status
        is_new = true
        $.each(cars[route['name']], function(car_index,car){
          if(Math.abs(car.running_time - new_car.running_time)<=240){
            is_new = false
            if(cars[route['name']][car_index].loc < new_car.loc){
              cars[route['name']][car_index].loc = new_car.loc
            }
            cars[route['name']][car_index].speed = new_car.speed
            cars[route['name']][car_index].running_time = new_car.running_time
            cars[route['name']][car_index].time_stamp = new_car.time_stamp
            //return(true)
          }
        })
        if(is_new){
          draw_car(new_car)
          cars[route['name']].push(new_car)
        }
      })
    }
    //draw_cars(route)
	log_info(route.ID + ' ' + route.name + ' arriving data loaded.')
  })
}

function log_info(str){
  $("#log_canvas").stop().fadeTo(0,0.9);
  $("#log_canvas").text(str);
  $("#log_canvas").append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
  setTimeout(function(){$("#log_canvas").fadeTo(5000,0)},5000)
}


/* Route query & processing related functions*/
var routes;    // list
current_routes = [];    // list
var stops;    // dict
var x;
cars = []
color = {"1A":'#0575cb',"1B":'#0575cb',"2A":"#e4142c","2B":"#e4142c","3":"#5e2c85","4A":"#669933","4B":"#669933","5A":"#e15822","5B":"#e15822","6A":"#f0436e","6B":"#f0436e","7":"#f4a91a","8":"#00afad","12":"#df8f1c","13":"#a0a0a0","14":"#231f20","15":"#f06b1e","16":"#995727","17":"#0099ff","18":"#272063","19":"#d13632","20":"#b02491","21":"#8dc83f","23":"#00AA59","27":"#55B340"}
$(document).ready(function(){
  map_initialize();
  $.getJSON("data/stops.json",{},function(Stops){
    stops = Stops
    for(stop in stops){
      stops[stop].activated = false
	  draw_stop(stop)
    }
	log_info('Stops data parsed successfully.')
  //});
  //stops = getJSON("data/stops.json")
  //$.ajax({
    //url: "data/stops.json",
       //async: false,
       //dataType: 'json',
       //success: function(Stops){stops = Stops}
  //});
  //$.getJSON("data/routes.json",{},function current(Routes){
  
    $.getJSON("data/routes.json",{},function(Routes){
      routes = Routes;
      routes.forEach(function(route){
        route.activated = false;
        route.click_activated = false;
        route.web_activated = false;
      })
	  log_info('Routes data parsed successfully.')
      icon_initialize();
      running_info_initialize();
      draw_current_routes();
      route_info()
      
      current_routes.forEach(find_car);    // TODO
      //setTimeout(animate, 5000);
      animate()
    });
  //running_info_initialize(getJSON("/data/routes.json"))
  //$.ajax({
    //url: "/data/routes.json",
       //async: false,
       //dataType: 'json',
       //success: function(Routes) {running_info_initialize(Routes)}});
  
  //console.log(routes);
  });
});
