#!/usr/bin/python
# 
# PiTextReader - Raspberry Pi Printed Text-to-Speech Reader
#
# Allows sight impaired person to have printed text read using
# OCR and text-to-speech.
#
# Normally run by pi crontab at bootup
# Turn off by commenting out @reboot... using $ crontab -e; sudo reboot
# Manually run using $ python pitextreader.py
#
# This is a simplistic (i.e. not pretty) python program
# Just runs cmd-line pgms raspistill, tesseract-ocr, flite to do all the work
#
# Version 1.0 2018.02.10 - initial release - rgrokett
# v1.1 - added some text cleanup to improve reading
# v1.2 - removed tabs
#
# http://kd.grokett.com/
#
# License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html
#
 
import RPi.GPIO as GPIO
import os, sys
import subprocess
import threading
import time 


##### USER VARIABLES
DEBUG   = 0 # Debug 0/1 off/on (writes to debug)
SPEED   = 1.0   # Speech speed, 0.5 - 2.0 
VOLUME  = 90    # Audio volume

# OTHER SETTINGS
SOUNDS  = "/home/pi/PiTextReader/sounds/" # Directory for sound effect(s)
CAMERA  = "raspistill -cfx 128:128 --awb auto -rot 180 -t 500 -o /tmp/image.jpg"

# GPIO BUTTONS
BTN1    = 24    # The button!
LED     = 18    # The button's LED!


### FUNCTIONS
# Thread controls for background processing
class RaspberryThread(threading.Thread):
    def __init__(self, function):
        self.running = False
        self.function = function
        super(RaspberryThread, self).__init__()

    def start(self):
        self.running = True
        super(RaspberryThread, self).start()

    def run(self):
        while self.running:
            self.function()

    def stop(self):
        self.running = False 

# LED ON/OFF
def led(val):   
    if val:
       GPIO.output(LED,GPIO.HIGH)
    else:
       GPIO.output(LED,GPIO.LOW)
    
# PLAY SOUND
def sound(val): # Play a sound
    time.sleep(0.2)
    cmd = "/usr/bin/aplay -q "+str(val)
    os.system(cmd)
    return
 
# SPEAK STATUS
def speak(val): # TTS Speak
    cmd = "/usr/bin/flite -voice awb --setf duration_stretch="+str(SPEED)+" -t \""+str(val)+"\""
    os.system(cmd)
    return 

# SET VOLUME
def volume(val): # Set Volume for Launch
    vol = int(val)
    cmd = "sudo amixer -q sset PCM,0 "+str(vol)+"%"
    os.system(cmd)
    return 

# TEXT CLEANUP
def cleanText():
    cmd = "sed -e 's/\([0-9]\)/& /g' -e 's/[[:punct:]]/ /g' -e 'G' -i /tmp/text.txt"
    os.system(cmd)
    return
    
# Play TTS (Allow Interrupt)
def playTTS():
    global current_tts
    current_tts=subprocess.Popen(['/usr/bin/flite','-voice','awb','-f', '/tmp/text.txt'],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,close_fds=True)
    # Kick off stop audio thread 
    rt.start()
    # Wait until finished speaking (unless interrupted)
    current_tts.communicate()
    return


# Stop TTS (with Interrupt)
def stopTTS():
    global current_tts
    # If button pressed, then stop audio
    if GPIO.input(BTN1) == GPIO.LOW:
        #current_tts.terminate()
        current_tts.kill()
        time.sleep(0.5)
    return 

# GRAB IMAGE AND CONVERT
def getData():
    led(0) # Turn off Button LED

    # Take photo
    sound(SOUNDS+"camera-shutter.wav")
    cmd = CAMERA
    os.system(cmd)

    # OCR to text
    speak("now working. please wait.")
    cmd = "/usr/bin/tesseract /tmp/image.jpg /tmp/text"
    os.system(cmd)
    
    # Cleanup text
    cleanText()

    # Start reading text
    playTTS()
    return


######
# MAIN
######
try:
    global rt
    # Setup GPIO buttons
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings (False)
     
    GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(LED, GPIO.OUT) 
    
    # Threaded audio player
    #rt = RaspberryThread( function = repeatTTS ) # Repeat Speak text
    rt = RaspberryThread( function = stopTTS ) # Stop Speaking text
    
    volume(VOLUME)
    speak("OK, ready")
    led(1)
    
    while True:
       if GPIO.input(14) == GPIO.HIGH:
            getData()
            rt.stop()
            rt = RaspberryThread( function = stopTTS ) # Stop Speaking text
            led(1)
            time.sleep(0.5)  
            time.sleep(0.2) 
    
except KeyboardInterrupt:

