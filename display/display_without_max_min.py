# Done:
# Display

from notsmb import notSMB
bus = notSMB(int('1'))
import sys
import os
import glob
import time
import MySQLdb as mdb
import math
import time
import decimal
import ConfigParser

import Adafruit_CharLCD as LCD
lcd = LCD.Adafruit_CharLCDPlate()

import logging
logging.basicConfig(filename='/home/pi/heating_log/error_display.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

Config = ConfigParser.ConfigParser()
Config.read("./config_heating.ini")
Config.sections()

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

serverip = ConfigSectionMap("SectionOne")['ip']
username = ConfigSectionMap("SectionOne")['name']
userpass = ConfigSectionMap("SectionOne")['pass']
schema = ConfigSectionMap("SectionOne")['schema']

CURRENT = 0
sensor_list=[]
G_current_room=""
G_current_temp="" 
G_target_temp= 0.000
G_current_temp=""
G_display_temp=""

def select_sql(command):
    """Will execute a select command onto the pi schema on 192.168.1.100 and return the value"""
    logging.debug("Running Select sql "+str(command))
    try:
## host, userid, password, database instance
      con = mdb.connect(serverip, username, userpass, schema);
      cursor = con.cursor()
        
      sql = command
      cursor.execute(sql)
      return cursor.fetchall()
           
      con.close()

    except mdb.Error, e:
      logger.error(e)
      
def insert_sql(command):
    """Will execute an insert or delete command onto the pi schema on 192.168.1.100 and commit changes"""
    logging.debug("Running insert sql "+str(command))
    try:
## host, userid, password, database instance
      
      con = mdb.connect(serverip, username, userpass, schema);
      cursor = con.cursor()
        
      sql = command
      cursor.execute(sql)
      sql = " commit;"
      cursor.execute(sql)
           
      con.close()

    except mdb.Error, e:
      logger.error(e)
      
def on_left_press():
    
    global CURRENT
    global sensor_list
    number_of_sensors=len(sensor_list)-1
    logging.debug("taking 1 away from curr sensor "+str(CURRENT))
    CURRENT -= 1
    if (CURRENT<0):
        CURRENT = number_of_sensors
    
def on_right_press():
    
    global CURRENT
    global sensor_list
    number_of_sensors=len(sensor_list)-1
    logging.debug("adding 1 to curr sensor "+str(CURRENT))
    CURRENT += 1
    if (CURRENT>number_of_sensors):
        CURRENT = 0

def on_up_press():
    
    global CURRENT
    global G_target_temp
    global sensor_list
    logging.debug("Raising target temp of curr sensor "+str(CURRENT))
    sensor = sensor_list[CURRENT]
    G_target_temp += decimal.Decimal('0.5')
    insert_sql("update current set target="+str(G_target_temp)+" where sensor = "+"'"+sensor[0]+"'")

    
def on_down_press():
    
    global CURRENT
    global G_target_temp
    global sensor_list
    logging.debug("Dropping target temp of curr sensor "+str(CURRENT))
    sensor = sensor_list[CURRENT]
    G_target_temp -= decimal.Decimal('0.5')
    insert_sql("update current set target="+str(G_target_temp)+" where sensor = "+"'"+sensor[0]+"'")
    
         
def get_current_sensors():
    return select_sql("select sensors from sensor_master where current = 1")
    
    
def get_room_details():
    global CURRENT
    global G_current_room 
    global G_current_temp 
    global G_target_temp
    global sensor_list
    current_room_temp= select_sql("SELECT room,last_reading,target FROM view_display WHERE sensor = '{0}'".format(sensor_list[CURRENT][0]))
    G_current_room= current_room_temp[0][0]
    G_current_temp= current_room_temp[0][1]
    G_target_temp = current_room_temp[0][2]
    
    
def update_screen():
    global G_current_room 
    global G_current_temp 
    global G_target_temp
    global G_display_temp
    G_display_temp= G_target_temp
    lcd.clear()
    display_message=('Room:' + G_current_room +'\n'+ 'C:' +str("%.1f" % G_current_temp)+ '/T:'+str("%.1f" %G_target_temp))
    lcd.message(display_message)
    get_colour()

def get_colour():
    global G_current_temp 
    global G_target_temp
    if G_current_temp < G_target_temp:
    #blue
        lcd.set_color(0.0, 0.0, 1.0)
    elif G_current_temp > G_target_temp:
    #red
        lcd.set_color(1.0, 0.0, 0.0)
    elif G_current_temp == G_target_temp:
    #green
        lcd.set_color(0.0, 1.0, 0.0)
    
    
def screen_off():
    lcd.clear()
    lcd.noDisplay()
                
def main():
    global CURRENT
    global sensor_list
    global G_current_room 
    global G_current_temp 
    global G_target_temp
    global G_display_temp
    loops = 0
    
    sensor_list=get_current_sensors()
    
    buttons = ( (LCD.SELECT, 'Select'),
            (LCD.LEFT,   'Left'  ),
            (LCD.UP,     'Up'    ),
            (LCD.DOWN,   'Down'  ),
            (LCD.RIGHT,  'Right' ) )

       
    get_room_details()
    update_screen()
    
    while True:
        while loops < 30:
            # Loop through each button and check if it is pressed.
            for button in buttons:
                if lcd.is_pressed(button[0]):
                    # Button is pressed, change the message and backlight.
                    if button[0] == int(0):
                        print 'select'
                    elif button[0] == int(1):
                        # 'right'
                        on_right_press()
                        get_room_details()
                        update_screen()
                        loops = 0
                    elif button[0] == int(2):
                        # 'down'
                        on_down_press()
                        get_room_details()
                        update_screen()
                        loops = 0
                    elif button[0] == int(3):
                        # 'up'
                        on_up_press()
                        get_room_details()
                        update_screen()
                        loops = 0
                    elif button[0] == int(4):
                        # 'left'
                        on_left_press()
                        get_room_details()
                        update_screen()
                        loops = 0
                    else:
                        logging.warning("unknown button pressed "+button[0])
                                                        
            time.sleep(0.3)
            loops=loops+1
        lcd.clear()
        lcd.set_backlight(0)
        get_room_details()
        if (G_display_temp != G_target_temp):
            update_screen()
        loops = 0
           
if __name__ == "__main__":
    main()
