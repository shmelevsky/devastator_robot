from flask import Flask, render_template, url_for, jsonify, request, Response
from werkzeug.contrib.fixers import ProxyFix
import subprocess
import RPi.GPIO as GPIO
from gpiozero import Robot, RGBLED
from time import time, sleep
import time
import os
import pygame
import threading


GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 24
GPIO_ECHO = 18
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
robot = Robot(left=(16, 12), right=(21, 20))
led = RGBLED(red=27, green=22, blue=17)
servoPIN_h = 8
servoPIN_v = 25
GPIO.setup(servoPIN_h, GPIO.OUT)
GPIO.setup(servoPIN_v, GPIO.OUT)
speed = 0.5
cur_color = 'green'


class ServoMotion:
    positions_horizontal = {
        1: 2.5,
        2: 4.5,
        3: 7,
        4: 9.5,
        5: 11.5,
    }

    positions_vertical = {
        1: 4,
        2: 7,
        3: 8.7,
        4: 9.8
    }

    def __init__(self):
        self.cur_h_position = 3
        self.cur_v_position = 3
        servo_v = GPIO.PWM(servoPIN_v, 50)
        servo_v.start(self.positions_vertical[self.cur_v_position])
        sleep(0.3)
        servo_v.stop()
        del servo_v
        servo_h = GPIO.PWM(servoPIN_h, 50)
        servo_h.start(self.positions_horizontal[self.cur_h_position])
        sleep(0.3)
        servo_h.stop()
        del servo_h

    def change_position(self, button_direction):
        if button_direction == 'right':
            if self.cur_h_position == 1:
                return
            else:
                self.cur_h_position -= 1
                servo_h = GPIO.PWM(servoPIN_h, 50)
                servo_h.start(self.positions_horizontal[self.cur_h_position])
                sleep(0.3)
                servo_h.stop()
                del servo_h
                return
        elif button_direction == 'left':
            if self.cur_h_position == 5:
                return
            else:
                self.cur_h_position += 1
                servo_h = GPIO.PWM(servoPIN_h, 50)
                servo_h.start(self.positions_horizontal[self.cur_h_position])
                sleep(0.3)
                servo_h.stop()
                del servo_h
                return
        elif button_direction == 'up':
            if self.cur_v_position == 1:
                return
            else:
                self.cur_v_position -= 1
                servo_v = GPIO.PWM(servoPIN_v, 50)
                servo_v.start(self.positions_vertical[self.cur_v_position])
                sleep(0.3)
                servo_v.stop()
                del servo_v
                return
        elif button_direction == 'down':
            if self.cur_v_position == 4:
                return
            else:
                self.cur_v_position += 1
                servo_v = GPIO.PWM(servoPIN_v, 50)
                servo_v.start(self.positions_vertical[self.cur_v_position])
                sleep(0.3)
                servo_v.stop()
                del servo_v
                return
        elif button_direction == 'middle':
            self.__init__()
            return


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
    updown = False
    leftright = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                position = float('%.2f' % event.value)
                if event.axis == 3:
                    if not leftright:
                        if position != 0.0:
                            updown = True
                        if position < 0:
                            robot.forward(speed=position*-1)
                        elif position > 0:
                            robot.backward(speed=position)
                        elif position == 0.0:
                            updown = False
                            robot.stop()
                elif event.axis == 0:
                    if not updown:
                        if position != 0.0:
                            leftright = True
                        if position < 0:
                            robot.left(speed=position*-1)
                        elif position > 0:
                            robot.right(speed=position)
                        elif position == 0.0:
                            leftright = False
                            robot.stop()

        sleep(0.01)


def set_new_color():
    colors = {
        'red': (1, 0, 0),
        'green': (0, 1, 0),
        'blue': (0, 0, 1),
        'yellow': (1, 1, 0)
    }
    led.color = colors[cur_color]

def ping_server():
    cmd = ['/usr/bin/fping  -q -B  1 -C 1 -p 500 -r 5 -t 500  10.7.10.1']
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


led_demo()
led.green = 1
servo_motion = ServoMotion()
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
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
        return jsonify(ping_server())


@app.route('/get_distance', methods=['POST'])
def get_distance():
    if request.method == 'POST':
        return jsonify(int(m_distance()))


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


@app.route('/servo', methods=['POST'])
def servo():
    if request.method == 'POST':
        direction = request.json['servo']
        servo_motion.change_position(direction)
        return Response(status=200)




app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=8080)
