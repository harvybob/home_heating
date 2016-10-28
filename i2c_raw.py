#!/usr/bin/env python

import io
import fcntl

# i2c_raw.py
# 2016-02-22
# Public Domain

I2C_SLAVE=0x0703

class i2c:


   def __init__(self, device, bus):

      self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
      self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

      # set device address

      fcntl.ioctl(self.fr, I2C_SLAVE, device)
      fcntl.ioctl(self.fw, I2C_SLAVE, device)

   def write(self, data):
      if type(data) is list:
         data = bytes(data)
      self.fw.write(data)

   def read(self, count):
      return self.fr.read(count)

   def close(self):
      self.fw.close()
      self.fr.close()

if __name__ == "__main__":

   import time
   import i2c_raw
   
   dev = i2c_raw.i2c(0x32, 1) # device 0x32, bus 1

   for j in range(10,18): # 10 to 17
      print "switching relay : "+str(j)
      dev.write(bytearray([j,1,0,1]))
      time.sleep(.2)
      dev.write(bytearray([j,0,0,1]))
      time.sleep(.2)

   dev.close()
