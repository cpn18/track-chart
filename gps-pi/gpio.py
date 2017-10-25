from time import sleep
import RPi.GPIO as GPIO

GPIO23=16

GPIO.setmode(GPIO.BOARD)

GPIO.setup(GPIO23, GPIO.IN)

while True:

# state toggle button is pressed
  if ( GPIO.input(GPIO23) == True ):
    print("pressed B1 ")

  sleep(0.2);
