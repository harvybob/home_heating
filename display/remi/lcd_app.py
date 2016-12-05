import remi.gui as gui
from remi.gui import to_pix
from remi import start, App
from threading import Timer

import sys
import os
import glob
import time
import MySQLdb as mdb
import math
import time
import decimal
import logging
logging.basicConfig(filename='../../heating_log/error_remi.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

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
      con = mdb.connect('192.168.1.100', 'pi', 'rpi', 'pi');
      #con = mdb.connect('192.168.2.2', 'pi', 'rpi', 'pi');
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
      con = mdb.connect('192.168.1.100', 'pi', 'rpi', 'pi');
      #con = mdb.connect('192.168.2.2', 'pi', 'rpi', 'pi');
      cursor = con.cursor()
        
      sql = command
      cursor.execute(sql)
      sql = " commit;"
      cursor.execute(sql)
           
      con.close()

    except mdb.Error, e:
      logger.error(e)
      
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
      
      

class LCDApp(App):
    def __init__(self, *args):
        super(LCDApp, self).__init__(*args, static_paths=('./res/',))

    def main(self):
        mainContainerWidth = 400 #will use this later to arrange buttons position
        self.mainContainer = gui.VBox(width=mainContainerWidth, height=600)
        
        self.imageRoom = gui.Image('./room_images/room.png', height=300)
        #suggestion: in order to change the displayed image you can do 
        #self.imageRoom.attributes['src'] = './res/new_image.png'
        self.mainContainer.append(self.imageRoom)
        
        #here we builds info labels and container
        labelsContainer = gui.Widget(width="100%", height=50) #the container is of type Widget, allowing to define custom position for each contained item
        self.mainContainer.append(labelsContainer)
        labelsContainer.style['position'] = 'relative' #this is important in order to obtain an aboslute positioning

        w=75
        h=25
        lblRoomName = gui.Label('Room:', width=w, height=h)
        self.lblRoomNameValue = gui.Label('living', width=w, height=h)
        
        lblCurrentTemperature = gui.Label('Current:', width=w, height=h)
        self.lblCurrentTemperatureValue = gui.Label('21 C', width=w, height=h)
        
        lblTargetTemperature = gui.Label('Target:', width=w, height=h)
        self.lblTargetTemperatureValue = gui.Label('22.5 C', width=w, height=h)
        
        #setup of the labels position
        lblRoomName.style['left'] = '5px'
        lblRoomName.style['top'] = '0px'
        lblRoomName.style['position'] = 'absolute'
        self.lblRoomNameValue.style['left'] = '80px'
        self.lblRoomNameValue.style['top'] = '0px'
        self.lblRoomNameValue.style['position'] = 'absolute'
        self.lblRoomNameValue.style['font-weight'] = 'bold'
        
        lblCurrentTemperature.style['left'] = '255px'
        lblCurrentTemperature.style['top'] = '0px'
        lblCurrentTemperature.style['position'] = 'absolute'
        self.lblCurrentTemperatureValue.style['left'] = '330px'
        self.lblCurrentTemperatureValue.style['top'] = '0px'
        self.lblCurrentTemperatureValue.style['position'] = 'absolute'
        self.lblCurrentTemperatureValue.style['font-weight'] = 'bold'
        
        lblTargetTemperature.style['left'] = '255px'
        lblTargetTemperature.style['top'] = '25px'
        lblTargetTemperature.style['position'] = 'absolute'
        self.lblTargetTemperatureValue.style['left'] = '330px'
        self.lblTargetTemperatureValue.style['top'] = '25px'
        self.lblTargetTemperatureValue.style['position'] = 'absolute'
        self.lblTargetTemperatureValue.style['font-weight'] = 'bold'
        
        #inserting the labels in their container
        labelsContainer.append(lblRoomName)
        labelsContainer.append(self.lblRoomNameValue)
        labelsContainer.append(lblCurrentTemperature)
        labelsContainer.append(self.lblCurrentTemperatureValue)
        labelsContainer.append(lblTargetTemperature)
        labelsContainer.append(self.lblTargetTemperatureValue)
        
        
        #here we build buttons and container
        buttonsContainer = gui.Widget(width="100%", height=150)
        self.mainContainer.append(buttonsContainer)
        buttonsContainer.style['position'] = 'relative' #this is important in order to obtain an aboslute positioning
        btWidth = 50
        btHeight = 50
        self.btUp = gui.Button('+', width=btWidth, height=btHeight)
        self.btDown = gui.Button('-', width=btWidth, height=btHeight)
        self.btRight = gui.Button('>', width=btWidth, height=btHeight)
        self.btLeft = gui.Button('<', width=btWidth, height=btHeight)
        
        self.btUp.set_on_click_listener(self, "on_click_up")
        self.btDown.set_on_click_listener(self, "on_click_down")
        self.btRight.set_on_click_listener(self, "on_click_right")
        self.btLeft.set_on_click_listener(self, "on_click_left")
        
        self.btUp.style['left']=to_pix(mainContainerWidth/2-btWidth/2)
        self.btUp.style['top']=to_pix(0)
        self.btUp.style['position'] = 'absolute'
        
        self.btDown.style['left']=to_pix(mainContainerWidth/2-btWidth/2)
        self.btDown.style['top']=to_pix(btHeight*2)
        self.btDown.style['position'] = 'absolute'
        
        self.btRight.style['left']=to_pix(mainContainerWidth/2+btWidth/2)
        self.btRight.style['top']=to_pix(btHeight)
        self.btRight.style['position'] = 'absolute'
        
        self.btLeft.style['left']=to_pix(mainContainerWidth/2-btWidth*3/2)
        self.btLeft.style['top']=to_pix(btHeight)
        self.btLeft.style['position'] = 'absolute'
        
        buttonsContainer.append(self.btUp)
        buttonsContainer.append(self.btDown)
        buttonsContainer.append(self.btRight)
        buttonsContainer.append(self.btLeft)

        get_room_details()
        
        #here we start a timer
        Timer(1, self.update).start()
        
        # returning the root widget
        return self.mainContainer

    # listener function
    def on_click_up(self):
        global CURRENT
        global G_target_temp
        global sensor_list
        logging.debug("Raising target temp of curr sensor "+str(CURRENT))
        sensor = sensor_list[CURRENT]
        G_target_temp += decimal.Decimal('0.5')
        insert_sql("update current set target="+str(G_target_temp)+" where sensor = "+"'"+sensor[0]+"'")
        
    # listener function
    def on_click_down(self):
        global CURRENT
        global G_target_temp
        global sensor_list
        logging.debug("Dropping target temp of curr sensor "+str(CURRENT))
        sensor = sensor_list[CURRENT]
        G_target_temp -= decimal.Decimal('0.5')
        insert_sql("update current set target="+str(G_target_temp)+" where sensor = "+"'"+sensor[0]+"'")
    
    # listener function
    def on_click_right(self):
        global CURRENT
        global sensor_list
        number_of_sensors=len(sensor_list)-1
        logging.debug("adding 1 to curr sensor "+str(CURRENT))
        CURRENT += 1
        if (CURRENT>number_of_sensors):
            CURRENT = 0
        
    # listener function
    def on_click_left(self):
        global CURRENT
        global sensor_list
        number_of_sensors=len(sensor_list)-1
        logging.debug("taking 1 away from curr sensor "+str(CURRENT))
        CURRENT -= 1
        if (CURRENT<0):
            CURRENT = number_of_sensors
       
    def update(self):
        #the code written here is executed each second
        global G_current_room 
        global G_current_temp 
        global G_target_temp
        global G_display_temp
        G_display_temp= G_target_temp
        display_message=('Room:' + G_current_room +'\n'+ 'C:' +str("%.1f" % G_current_temp)+ '/T:'+str("%.1f" %G_target_temp))
        lcd.message(display_message)
        #get_colour()
        self.lblRoomNameValue.set_text(G_current_room)
        self.lblCurrentTemperatureValue.set_text(str("%.1f" % G_current_temp))
        self.lblTargetTemperatureValue.set_text(str("%.1f" %G_target_temp))
        
        if G_current_temp < G_target_temp:
        #blue
            self.lblCurrentTemperatureValue.style['color']='blue'
        elif G_current_temp > G_target_temp:
        #red
            self.lblCurrentTemperatureValue.style['color']='red'
        elif G_current_temp == G_target_temp:
        #green
            self.lblCurrentTemperatureValue.style['color']='green'
        Timer(1, self.update).start()

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(LCDApp, debug=True)
