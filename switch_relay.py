import sys
import signal
import i2c_raw
import MySQLdb as mdb
import time
import ConfigParser
import logging
logging.basicConfig(filename='./heating_log/error_switch_relay.log', level=logging.INFO,
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




def handle_ctrl_c(signal, frame):
    print "Exiting heating"
    sys.exit(130) # 130 is standard exit code for ctrl-c

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

def new_move_sensor(move_sensor, table_from, table_to, off):
    """Will move sensor value from one table to another"""
    """ sensor to move, table to move from, table to move to, and expected new status"""
    # status: 0 is heating off
    # status: 1 is needs heat
    # status: 2 is heating on
    # status: 3 is turing off
    # status: -1 is an error occured 
    logging.debug(
        "move "+move_sensor+" from table "+table_from+" to "+table_to)

    insert_sql("INSERT INTO " + table_to + " (sensor) \
               VALUES('%s')" % \
               (move_sensor))
    insert_sql("DELETE FROM "+table_from+" WHERE sensor = '"+move_sensor+"'")
    if off == "turned_on":
        insert_sql("UPDATE sensor_master set required_status = 2 where sensors = '"+move_sensor+"'")
    elif off == "turned_off":
        insert_sql("UPDATE sensor_master set required_status = 0 where sensors = '"+move_sensor+"'")
    else:
        insert_sql("UPDATE sensor_master set required_status = -1 where sensors = '"+move_sensor+"'") 

def move_sensor(move_sensor,table_from,table_to):
    """Will move sensor value from one table to another"""
    logging.debug("move "+move_sensor+" from table "+table_from+" to "+table_to)

    insert_sql("INSERT INTO "+table_to+" (sensor) \
        VALUES ('%s')" % \
        (move_sensor))
    insert_sql("DELETE FROM "+table_from+" WHERE sensor = '"+move_sensor+"'")                     


def switch_relay(sensor):
    """Will look up relay number for a sensor and switch it"""
    relay_results=select_sql("SELECT relay,board FROM sensor_master WHERE sensors = '{0}'".format(sensor))
    for relay in relay_results:
        relay_no=int(relay[0])
        relay_board=int(relay[1])
        bv4627 = i2c_raw.i2c(relay_board, 1)
        logging.info("switching on relay "+str(relay_no)+" on board "+str(relay_board))
        bv4627.write(bytearray([relay_no,1,0,1]))
        time.sleep(.4)
        logging.info("switching off relay "+str(relay_no)+" on board "+str(relay_board))
        bv4627.write(bytearray([relay_no,0,0,1]))


def new_switch_heating():
    """Gets a list of current sensors from need_heating and moves them to heating_on or hot_enough  to off tables and switches relay"""
    logging.debug("Get list of current sensors from need_heating which need switching on")      
    on_sensor_list=select_sql("select sensor from need_heat")
    #on_sensor_list=select_sql("select sensors from sensor_master where current_status = 0 and required_status = 1")
    for i in range(0,len(on_sensor_list)):
            for sensor in on_sensor_list[i]:
                switch_relay(sensor)
                move_sensor(sensor,"need_heat","heating_on")

    logging.debug("Get list of current sensors from hot_enough which need switching off")      
    off_sensor_list=select_sql("select sensor from hot_enough")
    #off_sensor_list=select_sql("select sensors from sensor_master where current_status = 1 and required_status = 0")
    for i in range(0,len(off_sensor_list)):
            for sensor in off_sensor_list[i]:
                switch_relay(sensor)
                move_sensor(sensor,"hot_enough","heating_off")

def switch_heating():
    """Gets a list of current sensors from need_heating and moves them to heating_on or hot_enough  to off tables and switches relay"""
    logging.debug("Get list of current sensors from need_heating which need switching on")      
    on_sensor_list=select_sql("select sensor from need_heat")
    
    for i in range(0,len(on_sensor_list)):
            for sensor in on_sensor_list[i]:
                switch_relay(sensor)
                move_sensor(sensor,"need_heat","heating_on")

    logging.debug("Get list of current sensors from hot_enough which need switching off")      
    off_sensor_list=select_sql("select sensor from hot_enough")
    
    for i in range(0,len(off_sensor_list)):
            for sensor in off_sensor_list[i]:
                switch_relay(sensor)
                move_sensor(sensor,"hot_enough","heating_off")

def main():
    while True:
        switch_heating()
        signal.signal(signal.SIGINT, handle_ctrl_c)    
if __name__ == "__main__":
    main()
