import pygame
from time import sleep
from gpiozero import Robot

pygame.init()
#pygame.display.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
robot = Robot(left=(16, 12), right=(21, 20))
terminate = False
updown = False
leftright =False

while not terminate:
    try:
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
    except KeyboardInterrupt:
        terminate = True


