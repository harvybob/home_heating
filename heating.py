# Done:
# Heating switches based on temprature
# finds relay number for each sensor and switches
# Removed weezy relay switching - 29 nov 2016
# Changed target to max/min - 29 nov 2016
# Add max and min to current, and adjust view_current_on
#   and view_current_off to include max_target, min_target
# TODO:
# remove relay code
# record state of main relay or read this back from resistance - sepearte code.


import sys
import signal
#import i2c_raw
#bv4627 = i2c_raw.i2c(0x32, 1)  # device 0x32, bus 1
import MySQLdb as mdb
import ConfigParser
import logging
logging.basicConfig(filename='./heating_log/error_heating.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

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
    sys.exit(130)  # 130 is standard exit code for ctrl-c


def select_sql(command):
    """Will execute a select command onto the pi schema and return the value"""
    logging.debug("Running Select sql "+str(command))
    try:
        # host, userid, password, database instance
        con = mdb.connect(serverip, username, userpass, schema)
        cursor = con.cursor()
        sql = command
        cursor.execute(sql)
        return cursor.fetchall()
        con.close()
    except mdb.Error, e:
        logger.error(e)


def insert_sql(command):
    """Will execute an insert or delete command
       onto the pi schema and commit changes"""
    logging.debug("Running insert sql "+str(command))
    try:
        # host, userid, password, database instance
        con = mdb.connect(serverip, username, userpass, schema)
        cursor = con.cursor()
        sql = command
        cursor.execute(sql)
        sql = " commit;"
        cursor.execute(sql)
        con.close()
    except mdb.Error, e:
        logger.error(e)


def move_sensor(move_sensor, table_from, table_to, off):
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
    if off == "turn_off":
        insert_sql("UPDATE sensor_master set required_status = 3 where sensors = '"+move_sensor+"'")
    elif off == "need":
        insert_sql("UPDATE sensor_master set required_status = 1 where sensors = '"+move_sensor+"'")
    else:
        insert_sql("UPDATE sensor_master set required_status = -1 where sensors = '"+move_sensor+"'")
        
def check_heating():
    """Gets a list of current sensors from view_current_off/on
       and moves them to the need_heating or hot_enough tables"""
    logging.debug("Get list of current sensors from view_current_off which are cold")
    current_sensor_list = select_sql("select sensor from view_current_off where min_target > last_reading")
    for i in range(0, len(current_sensor_list)):
            for sensor in current_sensor_list[i]:
                move_sensor(sensor, "heating_off", "need_heat", "need")

    logging.debug("Get list of current sensors from view_current_on which are hot")
    current_sensor_list = select_sql("select sensor from view_current_on where max_target < last_reading")
    for i in range(0, len(current_sensor_list)):
            for sensor in current_sensor_list[i]:
                move_sensor(sensor, "heating_on", "hot_enough", "turn_off")


def main():
#    while True:
    check_heating()

    signal.signal(signal.SIGINT, handle_ctrl_c)
if __name__ == "__main__":
    main()
