
var xmlhttp;
xmlhttp=new XMLHttpRequest();

function init() {
    var button_forward = document.getElementById("forward");
    button_forward.addEventListener("touchstart", forward, false);
    button_forward.addEventListener("touchend", stop, false);
    var button_left = document.getElementById("left");
    button_left.addEventListener("touchstart", left, false);
    button_left.addEventListener("touchend", stop, false);
    var button_right = document.getElementById("right");
    button_right.addEventListener("touchstart", right, false);
    button_right.addEventListener("touchend", stop, false);
    var button_backward = document.getElementById("backward");
    button_backward.addEventListener("touchstart", backward, false);
    button_backward.addEventListener("touchend", stop, false);
    get_cur_speed();
    setInterval(function() {
        get_data('/get_ping', 'ping');
        get_data('/get_distance', 'distance' )
    }, 2000);
}

function forward() {
    xmlhttp.open("GET","/forward",true);
    xmlhttp.send();
}
function left() {
    xmlhttp.open("GET", "/left", true);
    xmlhttp.send();
}
function right() {
    xmlhttp.open("GET", "/right", true);
    xmlhttp.send();
}
function backward() {
    xmlhttp.open("GET", "/backward", true);
    xmlhttp.send();
}
function stop() {
    xmlhttp.open("GET","/stop", true);
    xmlhttp.send();
}


function get_data(url,selector_id) {

    var xmlhttp2;
    xmlhttp2=new XMLHttpRequest();
    xmlhttp2.open('POST', url, true);
    xmlhttp2.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xmlhttp2.onload = function () {
        if (xmlhttp2.status === 200) {
            var response = JSON.parse(xmlhttp2.responseText);
            document.getElementById(selector_id).innerHTML = selector_id+": "+response;
        } else if (xmlhttp2.status !== 200) {
            console.log('Request failed.  Returned status of ' + xmlhttp2.status);
            }
    };
    xmlhttp2.send();
}

function speed_changer() {
    var speed = document.getElementById('speed');
    if (Number(speed.innerHTML) === 4) {
        speed.innerHTML = '1';
    } else {
        speed.innerHTML = Number(speed.innerHTML) + 1;
    }
    var xmlhttp3;
    xmlhttp3 = new  XMLHttpRequest();
    xmlhttp3.open('POST', '/transmisson', true);
    xmlhttp3.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xmlhttp3.send(JSON.stringify({'speed': speed.innerHTML}));
}

function get_cur_speed() {
    var xmlhttp4;
    xmlhttp4 = new XMLHttpRequest();
    xmlhttp4.open('GET', '/transmisson', true);
    xmlhttp4.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xmlhttp4.onload = function () {
        if (xmlhttp4.status === 200) {
            var resp = JSON.parse(xmlhttp4.responseText);
            document.getElementById('speed').innerHTML = resp;
        } else if (xmlhttp2.status !== 200) {
            console.log('Request failed.  Returned status of ' + xmlhttp4.status);
        }
    };
    xmlhttp4.send();
}