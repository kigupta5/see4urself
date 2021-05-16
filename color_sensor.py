import RPi.GPIO as GPIO
import time
import os, sys
import logging
import subprocess
import threading


s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

SPEED   = 1.0   # Speech speed, 0.5 - 2.0

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering

GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 2 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 2 to be an input pin and set initial value to be pulled low (off)


# SPEAK STATUS
def speak(val): # Speak
    cmd = "/usr/bin/flite -voice awb --setf duration_stretch="+str(SPEED)+" -t \""+str(val)+"\""
    os.system(cmd)
    return 


def setup():
  #GPIO.setmode(GPIO.BCM)
  GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(s2,GPIO.OUT)
  GPIO.setup(s3,GPIO.OUT)
  print("\n")


def loop():
  temp = 1
  while(1):  

    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.LOW)
    time.sleep(0.3)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start 
    red  = NUM_CYCLES / duration   
   
    GPIO.output(s2,GPIO.LOW)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(0.3)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    blue = NUM_CYCLES / duration
    

    GPIO.output(s2,GPIO.HIGH)
    GPIO.output(s3,GPIO.HIGH)
    time.sleep(0.3)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
      GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start
    green = NUM_CYCLES / duration
    
    #speak("red value " + str(int(red)))
    #speak("green value " + str(int(green)))
    #speak("blue value " + str(int(blue)))
    print(str(red) + ":" + str(green) + ":" + str(blue))
    speak("The color is ")
      
    if red>green and red>blue:
      print("red")
      speak("red")
      temp=1
    elif green>red and green>blue:
      print("green")
      speak("green")
      temp=1
    elif blue>red and blue>green:
      print("blue")
      speak("blue")
      temp=1
    elif red>10000 and green>10000 and blue>10000 and temp==1:
      print("place the object.....")
      speak("place the object")
      temp=0
        
    if GPIO.input(15) != GPIO.HIGH:
        break
    
    


def endprogram():
    GPIO.cleanup()

if __name__=='__main__':
    
    setup()

    try:
        while True:
            #print(GPIO.input)
            if GPIO.input(15) == GPIO.HIGH:
                loop()
                print("button pressed")

    except KeyboardInterrupt:
        endprogram()
        









