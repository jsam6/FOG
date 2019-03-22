from pymongo import MongoClient
import sys,logging
from datetime import datetime
from mysql import connector
import traceback
from random import randint


# def rounder(t):
#     if t.hour == 6 :
#         return t.replace(minute=0, hour=6)
#     elif t.hour == 7:
#         return t.replace(minute=0, hour=8)
#     elif t.hour == 8:
#         return t.replace(minute=0, hour=8)
#     elif t.hour == 9:
#         return t.replace(minute=0, hour=10)
#     elif t.hour == 10:
#         return t.replace(minute=0, hour=10)
#     elif t.hour == 11:
#         return t.replace(minute=0, hour=12)
#     elif t.hour == 12:
#         return t.replace(minute=0, hour=12)
#     elif t.hour == 13:
#         return t.replace(minute=0, hour=14)
#     elif t.hour == 14:
#         return t.replace(minute=0, hour=14)
#     elif t.hour == 15:
#         return t.replace(minute=0, hour=16)
#     elif t.hour == 16:
#         return t.replace(minute=0, hour=16)
#     elif t.hour == 17:
#         return t.replace(minute=0, hour=18)
#     elif t.hour == 18:
#         return t.replace(minute=0, hour=18)
#     else:
#         return t.replace(minute=0, hour=18)

# date_today = datetime.today().date()

# time_now = datetime.now()
# # time_now = time_now.replace(minute=20, hour=9, second=0, microsecond=0)
# print(rounder(time_now).strftime("%H%M"))

ADD_DEFAULT_RECORD = "INSERT INTO fac_overview(facility_id, date, time, total_occupancy, current_occupancy) " \
             "VALUES(%s, %s, %s, %s, %s)"
CHECK_EXIST = "SELECT COUNT(*) FROM fac_overview WHERE facility_id = %s AND date = %s AND time = %s"

GET_FAC_NAME = "SELECT facility_id FROM facilities "


# Logger configuration
reload(sys)
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s')

def production_db_connection():
    global cnx_pd, cursor_pd 
    logging.info('Connecting to Production data schema...')
    cnx_pd = connector.connect(host="localhost", user="root", password="", database="fog", autocommit=True)
    cursor_pd = cnx_pd.cursor()

def add_default_record(facility_id,date, time):
    try:
        random_int_current = randint(1, 79)
        random_int_total = randint(80,100)
        cursor_pd.execute(ADD_DEFAULT_RECORD, (facility_id, date, time, random_int_total, random_int_current ))
        logging.info('DEFAULT RECORD ADDED: {}, DATE: {} TIME: {} IS ADDED'.format(facility_id, date, time))
    except:
        logging.error('DEFAULT RECORD: {}, DATE: {} IS FAILED TO ADD TO DATABASE. '.format(facility_id, date))

def check_exist(facility_id,date,time):
    cursor_pd.execute(CHECK_EXIST, (facility_id, date, time))
    return cursor_pd.fetchone()[0]

def get_fac_name():
    cursor_pd.execute(GET_FAC_NAME)
    return cursor_pd.fetchall() # [(u'Library',), (u'test',), (u'test1',), (u'test2',), (u'Gym',)]

if __name__ == '__main__':
    production_db_connection()
    fac_list = get_fac_name()
    # date_today = datetime(2018, 11, 10) # << testing
    date_today = datetime.today().date() # 2018-11-09

    time_list = ["0600","0800","1000","1200","1400","1600","1800"]
    for i in fac_list:
        fac_id = i[0]
        for time in time_list:
            if check_exist(fac_id, date_today, time) == 0:
                add_default_record(fac_id, date_today, time)
            else:
                logging.info('DEFAULT RECORD: {}, DATE: {} TIME: {} ALREADY EXIST IN DATABASE. '.format(fac_id, date_today, time))

