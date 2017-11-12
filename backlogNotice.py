import os
from bottle import route, run
import backlog
import ManHour
import ContactSummary
import threading
from datetime import datetime
from pytz import timezone
from datetime import timedelta


@route('/shortmeeting/')
def shortmeeting():
    th_me = threading.Thread(target=backlog.shortMeeting, name="th_me")
    th_me.start()
    return ''


@route('/manhour/')
def manhour():
    th_me_mh = threading.Thread(target=ManHour.getManHours, name="th_me_mh")
    th_me_mh.start()
    return ''


@route('/contactsummary/', method='GET')
def contactsummary():

    # パラメータ取得
    NOW = datetime.now(timezone('Asia/Tokyo'))
    #YESTERDAY = NOW + timedelta(days=-1)
    YESTERDAY = NOW
    tzJst = timezone("Asia/Tokyo")
    fromDate = datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, tzinfo=tzJst)
    toDate = datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, tzinfo=tzJst)

    th_me_cs = threading.Thread(target=ContactSummary.contactSummary(fromDate, toDate, True), name="th_me_cs")
    th_me_cs.start()

    todaysWeekDay = NOW.weekday()
    if todaysWeekDay == 0:
        LAST_MONDAY = NOW + timedelta(days=-7)
        fromDateWeek = datetime(LAST_MONDAY.year, LAST_MONDAY.month, LAST_MONDAY.day, 0, 0, 0, tzinfo=tzJst)
        toDateWeek = datetime(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day, 0, 0, 0, tzinfo=tzJst)
        th_me_cs_week = threading.Thread(target=ContactSummary.contactSummary(fromDateWeek, toDateWeek, False), name="th_me_cs_week")
        th_me_cs_week.start()

    return ''


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
