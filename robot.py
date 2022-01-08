from flask import Flask, render_template, url_for, jsonify, request, Response
from werkzeug.middleware.proxy_fix import ProxyFix
import subprocess
import RPi.GPIO as GPIO
from gpiozero import Robot, RGBLED
from time import time, sleep
import time
import os
import threading
from inputs import get_gamepad
from ina219 import INA219
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685


GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 24
GPIO_ECHO = 18
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
robot = Robot(left=(16, 12), right=(21, 20))
led = RGBLED(red=27, green=22, blue=17)
speed = 0.5
cur_color = 'green'
SHUNT_OHMS = 0.1
ina = INA219(SHUNT_OHMS)
ina.configure()


class ServoMotion:

    def __init__(self):
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c, address=0x41)
        self.pca.frequency = 50
        self.servo_h = servo.Servo(self.pca.channels[7])
        self.servo_v = servo.Servo(self.pca.channels[12])
        self.servo_h.set_pulse_width_range(500, 2300)
        self.servo_v.set_pulse_width_range(560, 1620)
        self.servo_h.angle = 90
        self.servo_v.angle = 120
        self.stop = False


    def left(self):
        threading.Thread(target=self.__make_thread, daemon=True, args=('left',)).start()

    def right(self):
        threading.Thread(target=self.__make_thread, daemon=True, args=('right',)).start()

    def up(self):
        threading.Thread(target=self.__make_thread, daemon=True, args=('up',)).start()

    def down(self):
        threading.Thread(target=self.__make_thread, daemon=True, args=('down',)).start()

    def __make_thread(self, direction):
        if direction in ['right', 'left']:
            serv = self.servo_h
        else:
            serv = self.servo_v

        if direction in ('left', 'down'):
            for angle in range(int(serv.angle), 180):
                serv.angle = angle
                sleep(0.01)
                if self.stop:
                    break
        if direction in ('right', 'up'):
            cur_position = int(serv.angle) 
            for angle in range(cur_position):
                serv.angle = cur_position - angle
                sleep(0.01)
                if self.stop:
                    break


servo_motion = ServoMotion()

def led_demo():
    for i in range(3):
        for n in range(101):
            led.green = n / 100
            sleep(0.01)
        if i == 2:
            break
        for n in reversed(range(101)):
            led.green = n / 100
            sleep(0.01)


def joy():
    while 1:
        events = get_gamepad()
        for event in events:
            if event.code == 'SYN_REPORT':
                continue
            if event.code == 'ABS_RZ':
                if event.state in range(0,128):
                    robot.forward(speed=1)
                if event.state in range(129,256):
                    robot.backward()
                if event.state == 128:
                    robot.stop()
            if event.code == 'ABS_X':
                if event.state in range(0,128):
                    robot.left()
                if event.state in range(129,256):
                    robot.right()
                if event.state == 127:
                    robot.stop()
            if event.code == 'ABS_HAT0X':
                if event.state == -1:
                    robot.left()
                if event.state == 1:
                    robot.right()
                if event.state == 0:
                    robot.stop()
            if event.code == 'ABS_HAT0Y':
                if event.state == -1:
                    robot.forward()
                if event.state == 1:
                    robot.backward()
                if event.state == 0:
                    robot.stop()


def set_new_color():
    colors = {
        'red': (1, 0, 0),
        'green': (0, 1, 0),
        'blue': (0, 0, 1),
        'yellow': (1, 1, 0)
    }
    led.color = colors[cur_color]


def ping_server():
    cmd = ['/usr/bin/fping  -q -B  1 -C 1 -p 500 -r 5 -t 500  192.168.88.1']
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ping = out.communicate()[1:][0].decode('UTF-8').split(':')[1]
    return ping


def m_distance():
    GPIO.output(GPIO_TRIGGER, True)
    sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance


def voltage(): 
    return "%.3f V" % ina.supply_voltage()


def current():
    return "%.3f mA" % ina.current()


tr = threading.Thread(name='led_demo', target=led_demo())
tr.setDaemon(True)
tr.start()

led.green = 1
tread = threading.Thread(name='joy', target=joy)
tread.setDaemon(True)
tread.start()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forward')
def forward():
    robot.forward(speed=speed)
    return Response(status=200)


@app.route('/left')
def left():
    robot.left(speed=speed)
    return Response(status=200)


@app.route('/right')
def right():
    robot.right(speed=speed)
    return Response(status=200)


@app.route('/backward')
def backward():
    robot.backward(speed=speed)
    return Response(status=200)


@app.route('/stop')
def stop():
    robot.stop()
    return Response(status=200)


@app.route('/get_ping', methods=['POST'])
def get_ping():
    if request.method == 'POST':
        return jsonify('%.3f ms' % float(ping_server()))


@app.route('/get_distance', methods=['POST'])
def get_distance():
    if request.method == 'POST':
        return jsonify('%.3f cm' % float(m_distance()))


@app.route('/get_voltage', methods=['POST'])
def get_voltage():
    if request.method == 'POST':
        return jsonify(voltage())


@app.route('/get_current', methods=['POST'])
def get_current():
    if request.method == 'POST':
        return jsonify(current())


@app.route('/transmisson', methods=['POST', 'GET'])
def transmission():
    global speed
    speeds = {
        1: 0.25,
        2: 0.5,
        3: 0.75,
        4: 1
    }
    if request.method == 'POST':
        speed = speeds[int(request.json['speed'])]
        return Response(status=200)
    if request.method == 'GET':
        speeds = dict(map(reversed, speeds.items()))
        return jsonify(speeds[speed])


@app.route('/set_color', methods=['POST', 'GET'])
def set_color():
    global cur_color
    if request.method == 'POST':
        cur_color = request.json['cur_color']
        set_new_color()
    if request.method == 'GET':
        return jsonify(cur_color)
    return Response(status=200)


@app.route('/power')
def power():
    return render_template('power.html')


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    if request.method == 'POST':
        if request.form['shutdown'] == 'do_shutdown':
            os.system(b'/sbin/shutdown now')
    return Response(status=200)


@app.route('/servo_l')
def servo_l():
    servo_motion.stop = False
    servo_motion.left()
    return Response(status=200)


@app.route('/servo_r')
def servo_r():
    servo_motion.stop = False
    servo_motion.right()
    return Response(status=200)

@app.route('/servo_u')
def servo_u():
    servo_motion.stop = False
    servo_motion.up()
    return Response(status=200)

@app.route('/servo_d')
def servo_d():
    servo_motion.stop = False
    servo_motion.down()
    return Response(status=200)


@app.route('/servo_s')
def servo_s():
    servo_motion.stop = True
    return Response(status=200)

@app.route('/servo_m')
def servo_m():
    servo_motion.servo_h.angle = 90
    servo_motion.servo_v.angle = 120
    return Response(status=200)



app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=8080)
