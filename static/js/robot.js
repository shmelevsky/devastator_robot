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


    var servo_right = document.getElementById("servo_r");
    servo_right.addEventListener("touchstart", servo_r, false);
    servo_right.addEventListener("touchend", servo_s, false);

    var servo_left = document.getElementById("servo_l");
    servo_left.addEventListener("touchstart", servo_l, false);
    servo_left.addEventListener("touchend", servo_s, false);

    var servo_up = document.getElementById("servo_u");
    servo_up.addEventListener("touchstart", servo_u, false);
    servo_up.addEventListener("touchend", servo_s, false);

    var servo_down = document.getElementById("servo_d");
    servo_down.addEventListener("touchstart", servo_d, false);
    servo_down.addEventListener("touchend", servo_s, false);

    get_cur_speed();
    get_cur_color();
    setInterval(function() {
        get_data('/get_ping', 'ping');
        get_data('/get_distance', 'distance' )
        get_data('/get_current', 'current' )
        get_data('/get_voltage', 'voltage' )
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


function servo_r() {
    xmlhttp.open("GET","/servo_r", true);
    xmlhttp.send();
}

function servo_l() {
    xmlhttp.open("GET","/servo_l", true);
    xmlhttp.send();
}

function servo_u() {
    xmlhttp.open("GET","/servo_u", true);
    xmlhttp.send();
}

function servo_d() {
    xmlhttp.open("GET","/servo_d", true);
    xmlhttp.send();
}

function servo_s() {
    xmlhttp.open("GET","/servo_s", true);
    xmlhttp.send();
}

function servo_m() {
    xmlhttp.open("GET","/servo_m",true);
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
            document.getElementById(selector_id).innerHTML = response;
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
        } else if (xmlhttp4.status !== 200) {
            console.log('Request failed.  Returned status of ' + xmlhttp4.status);
        }
    };
    xmlhttp4.send();

}
cur_color = 'green';
function set_color() {
    var xhtp;
    xhtp = new XMLHttpRequest();
    var color_el = document.getElementById('set_color');
    if (this.cur_color === 'green') {
        color_el.style.backgroundColor = "blue";
        this.cur_color = 'blue'
    } else if (this.cur_color === 'blue') {
        color_el.style.backgroundColor = 'red';
        this.cur_color = 'red'
    } else if (this.cur_color === 'red') {
        color_el.style.backgroundColor ='yellow';
        this.cur_color = 'yellow'
    } else if (this.cur_color === 'yellow') {
        color_el.style.backgroundColor = 'green';
        this.cur_color = 'green'
    }
    xhtp.open('POST', '/set_color', true);
    xhtp.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xhtp.send(JSON.stringify({'cur_color': this.cur_color}));
}

function get_cur_color() {
    var xhtp;
    xhtp = new XMLHttpRequest();
    xhtp.open('GET', '/set_color', true);
    xhtp.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xhtp.onload = function () {
        if (xhtp.status === 200) {
            var resp = JSON.parse(xhtp.responseText);
            document.getElementById('set_color').style.backgroundColor = resp;
        } else if (xhtp.status !== 200) {
            console.log('Request failed.  Returned status of ' + xhtp.status);
        }
    };
    xhtp.send();
}

