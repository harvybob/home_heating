#!/usr/bin/python
#Followed this guide:
# http://iot-projects.com/index.php?id=connect-ds18b20-sensors-to-raspberry-pi

#1st Feb - inital write
#3rd Feb - tidy up and add debug
#4th Feb - Comments for help
#29th Nov - Split to check what sensors are on this pi and if they are current then update.


import time
import os
import fnmatch
import MySQLdb as mdb
import ConfigParser
import logging
logging.basicConfig(filename='/home/pi/heating/heating_log/DS18B20_error.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

Main_sensor_list = []


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

def clear_sensors():
    """Will clear all tables using the insert_sql procedure"""
    logging.debug("Clearing tables ")
    #execute_sql("TRUNCATE TABLE current")
    insert_sql("TRUNCATE TABLE heating_off")
    insert_sql("TRUNCATE TABLE heating_on")
    insert_sql("TRUNCATE TABLE hot_enough")
    insert_sql("TRUNCATE TABLE need_heat")
    

def get_current_sensors():
    """Will get a list of current sensors from the database"""
    logging.debug("Get list of current sensors from sensor_master")      
    my_sensors = []
    my_current_sensors = []
    for file in os.listdir("/sys/bus/w1/devices"):
        if fnmatch.fnmatch(file, '28*'):
            my_sensors.append(file)

    for i in xrange(0,len(my_sensors)):
        if (select_sql("select sensors from sensor_master where sensors = '"+(my_sensors[i])+"' and current = 1")):
            my_current_sensors.append(my_sensors[i])
    
    return my_current_sensors
       
    

def get_reading(sensor):
    """Will get temprature reading of sensor"""
    logging.debug("Get temprature for sensor "+str(sensor))
    temperature = []
    IDs = []
  
    for filename in os.listdir("/sys/bus/w1/devices"):
      if fnmatch.fnmatch(filename, sensor):
        with open("/sys/bus/w1/devices/" + filename + "/w1_slave") as fileobj:
          lines = fileobj.readlines()
          if lines[0].find("YES"):
            pok = lines[1].find('=')
            temperature.append(float(lines[1][pok+1:pok+6])/1000)
            IDs.append(filename)
          else:
              logger.error("Error reading sensor with ID: %s" % (filename))
  
    if (len(temperature)>0):
        #insertDB(IDs, temperature)
        return (IDs[0],time.strftime("%Y-%m-%d"), time.strftime("%H:%M"), temperature[0])
    

def update_value(sensor):
    """Will insert the current temprature of a sensor into database table"""
    logging.debug("Insert sensor details into temp_log " + str(sensor))
    values_to_insert= get_reading(sensor)
    if (values_to_insert[3] < 7):
        logging.INFO( "value too low for sensor: " + str(values_to_insert[0]) + ". value read is: " + str(values_to_insert[3]))
        values_to_insert= get_reading(sensor)
    # returns in format of sensor, date, time, value
    insert_sql("INSERT INTO temp_log(sensor_id, date, time, value) \
        VALUES ('%s', '%s', '%s', '%s' );" % \
        (values_to_insert[0],values_to_insert[1],values_to_insert[2],values_to_insert[3]))
    logging.debug("Insert sensor details into current" + str(sensor))
    insert_sql("INSERT INTO current (sensor, target, last_reading, date, time) \
        VALUES ('%s', 20, '%s', '%s', '%s' ) \
        on duplicate key update last_reading='%s', date='%s', time='%s' " % \
        (values_to_insert[0],values_to_insert[3],values_to_insert[1],values_to_insert[2],values_to_insert[3],values_to_insert[1],values_to_insert[2]))
    

def main():

    #clear_sensors()
    Main_sensor_list=get_current_sensors()
    
    for i in range(0,len(Main_sensor_list)): 
        update_value(Main_sensor_list[i])
                        
if __name__ == "__main__":
    main()
