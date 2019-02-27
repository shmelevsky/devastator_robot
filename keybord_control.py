#!/usr/bin/env python3.5
import curses
from gpiozero import Robot, RGBLED
from time import sleep, time
import os
import threading
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 24
GPIO_ECHO = 18
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


class DfRobot:

    robot_lock = False
    dist_for_stop = 30  # in sm
    terminate = False

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.robot = Robot(left=(16, 12), right=(21, 20))
        self.led = RGBLED(red=27, green=22, blue=17)
        self.speed = 1
        self.speeds = {
            '1': 0.25,
            '2': 0.5,
            '3': 0.75,
            '4': 1
        }

    def led_demo(self):
        for i in range(3):
            for n in range(101):
                self.led.green = n / 100
                sleep(0.01)
            if i == 2:
                break
            for n in reversed(range(101)):
                self.led.green = n / 100
                sleep(0.01)

    def select_color(self):
        colors = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 1, 0),
            (1, 0, 1),
            (1, 1, 1),
            (0, 1, 1)
        )
        last_color = self.led.color
        self.led.off()
        index = colors.index(last_color)
        if index == 6:
            index = -1
        self.led.color = colors[index + 1]

    def m_distance(self):
        # set Trigger to HIGH
        GPIO.output(GPIO_TRIGGER, True)
        # set Trigger after 0.01ms to LOW
        sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
        start_time = time.time()
        stop_time = time.time()
        # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            start_time = time.time()
        # save time of arrival
        while GPIO.input(GPIO_ECHO) == 1:
            stop_time = time.time()
        # time difference between start and arrival
        time_elapsed = stop_time - start_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2
        return distance

    def ultrasonic(self):
        s = 0
        while not self.terminate:
            distance = self.m_distance()
            if distance < 0:
                continue
            print(distance)
            if distance < self.dist_for_stop:
                s += 1
                if s != 2:
                    continue
            if s == 2:
                last_color = self.led.color
                self.led.off()
                self.led.red = 1
                self.robot_lock = True
                self.robot.stop()
                sleep(0.1)
                #self.robot.backward(speed=0.5)
                while distance < (self.dist_for_stop + 10):
                    distance = self.m_distance()
                    print('AAAAA', distance)
                    sleep(0.5)
                self.robot.stop()
                self.robot_lock = False
                self.led.red = 0
                self.led.color = last_color
                curses.flushinp()
            sleep(0.3)
            s = 0
        return

    def control(self):
        self.tread = threading.Thread(name='ultrasonic', target=self.ultrasonic)
        self.tread.setDaemon(True)
        self.tread.start()

        while True:
            key = self.stdscr.getch()
            if self.robot_lock:
                continue
            if key in (ord('1'), ord('2'), ord('3'), ord('4')):
                self.speed = self.speeds[chr(key)]
            elif key == curses.KEY_UP:
                self.robot.forward(speed=self.speed)
            elif key == curses.KEY_DOWN:
                self.robot.backward(speed=self.speed)
            elif key == curses.KEY_RIGHT:
                self.robot.right(speed=self.speed)
            elif key == curses.KEY_LEFT:
                self.robot.left(speed=self.speed)
            elif key == ord('p'):
                self.robot.reverse()
            elif key == ord('s'):
                self.robot.stop()
            elif key == ord('c'):
                self.select_color()
            elif key == ord('S'):
                self.terminate = True
                self.tread.join()
                for gpio in [GPIO_ECHO, GPIO_TRIGGER, 16, 12, 21, 20, 27, 22, 17]:
                    GPIO.cleanup(gpio)
                os.system(b'/sbin/shutdown now')


if __name__ == '__main__':
    print('Running')
    try:
        df = DfRobot()
        df.led_demo()
        df.led.green = 1
        df.control()
    except KeyboardInterrupt:
        df.terminate = True
        df.tread.join()
        print('Tread ultrasonic is %s' % df.tread.is_alive())
        print('Interrupted by CTRl+C')
        # curses.nocbreak()
        # df.stdscr.keypad(0)
        # curses.echo()
        # curses.endwin()
        for gpio in [GPIO_ECHO, GPIO_TRIGGER, 16, 12, 21, 20, 27, 22, 17]:
            GPIO.cleanup(gpio)
