# Done:
# Update entries based on reading values from schedule table
# Holiday mode - works from global var
#
# TODO:
# Holiday mode - turn heating down till a set time for all rooms
#		Currently checks dates and turns off from globals.
#       Need to create table, and enter values - holiday mode, date, time
# Party mode - turn heating down for set time in 1 - many rooms
#		need to check date/time from database
#       Need to create table, and enter values - partymode mode, date, time, rooms to keep off
# Adjust timings to bring forward/back heating times

import sys
import os
import glob
import time
import datetime
import MySQLdb as mdb
import ConfigParser
import logging
logging.basicConfig(filename='/home/pi/heating/heating_log/error_scheduler.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

Config = ConfigParser.ConfigParser()
Config.read("././config_heating.ini")
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


Main_sensor_list = []
G_current_day = 0
G_current_date = "DD/MM/YYYY"
G_current_time = "00:00:00"
G_current_sensor=""
G_current_target_temp= 0.000
G_schedule_target_temp= 0.000
G_holiday_date = "DD/MM/YYYY"
G_holiday_time = "00:00:00"
G_holiday_mode = "Y"


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



def get_current_sensors():
    """Will get a list of current sensors from the database"""
    logging.debug("Get list of current sensors from sensor_master")      
    current_sensor_list=select_sql("select sensors from sensor_master where current = 1")
    return current_sensor_list
                

def get_now():
    """ Set current day and time values"""
    global G_current_day
    global G_current_time
    global G_current_date
    G_current_day = datetime.datetime.today().weekday()
    G_current_time= time.strftime("%H:%M")
    G_current_date = time.strftime("%d/%m/%Y")


def get_sensor_schedule_target():
    """ will find the new target value of a sensor and return it"""
    global G_current_day
    global G_current_time
    global G_current_sensor
    logging.debug("Get target temp if matching sensor date and time found") 
    local_schedule_target_temp= select_sql("SELECT target FROM heating_schedule WHERE sensors = '"+G_current_sensor+"' and Day = "+str(G_current_day)+" and time like '"+str(G_current_time)+"%'")
    
    try:
        if (len(local_schedule_target_temp) == 1):
            return local_schedule_target_temp[0][0]
    except ValueError:
        logging.debug("local_schedule_target+temp is zero ")
     
def get_sensor_current_target():
    """ will find the current target value of a sensor and return it"""
    global G_current_sensor
    logging.debug("Get current target temp if matching sensor found")         
    local_current_sensor=select_sql("SELECT target FROM current WHERE sensor = '"+G_current_sensor+"'")
    return local_current_sensor[0][0]


def holiday_mode_off():
    global G_current_date
    global G_current_time
    global G_holiday_date
    global G_holiday_time
    global G_holiday_mode
	
    logging.debug("")
    logging.debug("Current holiday mode: "+ G_holiday_mode + " Current holiday date: "+ G_holiday_date + " Current holiday time: "+ G_holiday_time)
    logging.debug("Current date: "+ G_current_date + " Current time time: "+ G_current_time)
    
    if G_holiday_date == G_current_date:
        if G_holiday_time == G_current_time:
            G_holiday_mode = "N"
            logging.info("Holiday Mode switched off on: "+ str(G_holiday_date) + " at " + str(G_holiday_time))
	
    logging.debug("Current holiday mode: "+ G_holiday_mode)
    logging.debug("")


def is_holiday_mode():
    global G_holiday_date
    global G_holiday_time
    global G_holiday_mode
    holiday_date = "DD/MM/YYYY"
    holiday_time = "00:00"
	
    holiday_mode=select_sql("SELECT * FROM holiday_mode")	
    if holiday_mode[0][0] == 1:
        G_holiday_mode = "Y"
        holiday_date=holiday_mode[0][1]
        holiday_time=holiday_mode[0][2]
        print holiday_date.strftime("%d/%m/%Y")
        print type(holiday_time)
        print holiday_time
        

def check_set_new_temp(sensor):
    logging.debug("")
    logging.debug("Time:"+ G_current_time)
    logging.debug("")            
    G_current_sensor = (Main_sensor_list[i][0])
    G_schedule_target_temp=get_sensor_schedule_target()
    logging.debug("")
    logging.debug("Current value of G_schedule_target_temp is: "+ str(G_schedule_target_temp))
    logging.debug("if value is None, then no result was returned from db")
    logging.debug("")
    G_current_target_temp=get_sensor_current_target()
    logging.debug("Current value of G_current_target_temp is: "+ str(G_current_target_temp))
    if (G_schedule_target_temp is not None) :
       # if nothing found in select then type is returned as none, ie no value at all
       # if a value is found then updates as required
        insert_sql("update current set target="+str(G_schedule_target_temp)+" where sensor = "+"'"+G_current_sensor+"'")
        G_current_target_temp=get_sensor_current_target()   
	
def main():
    global G_current_day
    global G_current_time
    global G_current_sensor
    global G_current_target_temp
    global G_schedule_target_temp
    
    
    Main_sensor_list=get_current_sensors()
    

    
    while True:
        for i in range(0,len(Main_sensor_list)): 
            get_now();
           # is_holiday_mode()
           # holiday_mode_off()
           
           #MOVE THIS TO OWN METHOD
            logging.debug("")
            logging.debug("Time:"+ G_current_time)
            logging.debug("")            
            G_current_sensor = (Main_sensor_list[i][0])
            G_schedule_target_temp=get_sensor_schedule_target()
            logging.debug("")
            logging.debug("Current value of G_schedule_target_temp is: "+ str(G_schedule_target_temp))
            logging.debug("if value is None, then no result was returned from db")
            logging.debug("")
            G_current_target_temp=get_sensor_current_target()
            logging.debug("Current value of G_current_target_temp is: "+ str(G_current_target_temp))
            
       
       
            if (G_schedule_target_temp is not None) :
           # if nothing found in select then type is returned as none, ie no value at all
           # if a value is found then updates as required
       
                insert_sql("update current set target="+str(G_schedule_target_temp)+" where sensor = "+"'"+G_current_sensor+"'")
                G_current_target_temp=get_sensor_current_target()
           #ALL THE WAY TO HERE     

        time.sleep(60)   
            
if __name__ == "__main__":
    main()
