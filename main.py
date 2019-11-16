# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
DOWN = True
MAGNETOFF = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

atLowTower = False
atHighTower = False

lowerTowerPosition = 60
upperTowerPosition = 76

arm = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
              steps_per_unit=200, speed=2)


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    armPosition = 0
    lastClick = time.clock()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if (currentTime - self.lastClick) > DEBOUNCE:
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        self.moveArm()

    def moveArm(self):
        global DOWN
        if DOWN:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            #sleep(.5)
            DOWN = False
            self.ids.armControl.text = "Arm Up"
        else:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            #sleep(.5)
            self.ids.armControl.text = "Arm Down"
            DOWN = True

    def toggleMagnet(self):
        global MAGNETOFF
        # MAGNETOFF = True

        if MAGNETOFF:
            cyprus.set_servo_position(2, 1)
            print("Magnet On")
            MAGNETOFF = False
            self.ids.magnetControl.text = "Off"
        else:
            cyprus.set_servo_position(2, 0.5)
            MAGNETOFF = True
            print("Magnet Off")
            self.ids.magnetControl.text = "On"

        # while True:
        #   if MAGNETOFF:
        #      cyprus.set_servo_position(2, 1)
        #     MAGNETOFF = False
        # if not (cyprus.read_gpio()) & 0b0001:
        #   if not MAGNETOFF:
        #      cyprus.set_servo_position(2, 0.5)
        #     MAGNETOFF = True
        # if not (cyprus.read_gpio()) & 0b0001:
        #    if atLowTower:
        #       cyprus.set_servo_position(2, 1)
        # if not (cyprus.read_gpio()) & 0b0010:
        #   if not MAGNETOFF:
        #      cyprus.set_servo_position(2, 0.5)
        #     MAGNETOFF = True
        # if not (cyprus.read_gpio()) & 0b0010:
        #    if atHighTower:
        #       cyprus.set_servo_position(2, 1)

    def auto(self):
        print("Run the arm automatically here")
        self.homeArm()
        arm.go_to_position(upperTowerPosition)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        cyprus.set_servo_position(2, 1)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        arm.go_to_position(lowerTowerPosition)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        cyprus.set_servo_position(2, 0.5)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        self.homeArm()


    def setArmPosition(self):
        global atLowTower
        global atHighTower
        position = self.ids.moveArm.value
        arm.start_go_to_position(-position)
        print(position)
        if position == lowerTowerPosition:
            atLowTower = True
        if position == upperTowerPosition:
            atHighTower = True

        print("Move arm here")

    def homeArm(self):
        arm.home(1)

    def isBallOnTallTower(self):
        print("Determine if ball is on the top tower")

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")

    def initialize(self):
        print("Home arm and turn off magnet")
        cyprus.initialize()
        cyprus.setup_servo(2)
        cyprus.set_servo_position(2, 0.5)
        arm.set_speed(.1)
        self.homeArm()
        arm.set_as_home()

        cyprus.setup_servo(1)


    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
