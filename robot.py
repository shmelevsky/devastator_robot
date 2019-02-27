from flask import Flask, render_template, redirect, jsonify, request
import subprocess
import RPi.GPIO as GPIO
from gpiozero import Robot, RGBLED
from time import time, sleep
import time

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 24
GPIO_ECHO = 18
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
robot = Robot(left=(16, 12), right=(21, 20))
led = RGBLED(red=27, green=22, blue=17)
speed = 0.5


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


led_demo()
led.green = 1


def ping_server():
    cmd = ['/usr/bin/fping  -q -B  1 -C 1 -p 500 -r 5 -t 500  82.193.109.230']
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forward')
def forward():
    robot.forward(speed=speed)
    return redirect('/')


@app.route('/left')
def left():
    robot.left(speed=speed)
    return redirect('/')


@app.route('/right')
def right():
    robot.right(speed=speed)
    return redirect('/')


@app.route('/backward')
def backward():
    robot.backward(speed=speed)
    return redirect('/')


@app.route('/stop')
def stop():
    robot.stop()
    return redirect('/')


@app.route('/get_ping', methods=['POST'])
def get_ping():
    if request.method == 'POST':
        return jsonify(ping_server())


@app.route('/get_distance', methods=['POST'])
def get_distance():
    if request.method == 'POST':
        return jsonify(m_distance())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
