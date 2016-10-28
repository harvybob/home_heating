import i2c_raw
bv4627 = i2c_raw.i2c(0x32, 1) # device 0x32, bus 1
import MySQLdb as mdb
import ConfigParser
import logging
logging.basicConfig(filename='./heating_log/error_heating.log', level=logging.INFO,
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




def switch_relay(sensor):
    """Will look up relay number for a sensor and switch it"""
    relay_results=select_sql("SELECT relay FROM sensor_master WHERE sensors = '{0}'".format(sensor))
    for relay in relay_results:
        relay_no=int(relay[0])
        logging.info("switching on relay "+str(relay_no))
        bv4627.write(bytearray([relay_no,1,0,1]))
        time.sleep(.4)
        logging.info("switching off relay "+str(relay_no))
        bv4627.write(bytearray([relay_no,0,0,1]))


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
