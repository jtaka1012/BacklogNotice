# encoding: utf-8
import os
from datetime import datetime
from dateutil import parser
from datasender import DataSender


# ENV_PARAM
BACKLOG_API_KEY = os.environ["BACKLOG_API_KEY"]


class BacklogCommon:

    # マイルストーン取得
    def getMileStones(self, projectId: str, UTC_TODAY: datetime, isALL: bool) -> dict:

        dataSender = DataSender()
        msParam = [
            ('apiKey', BACKLOG_API_KEY)
        ]
        MS_URL = '/api/v2/projects/' + projectId + '/versions'
        milestoneList = dataSender.sendDataToBacklog(msParam, MS_URL)

        resp = {}
        for milestone in milestoneList:
            print(milestone['name'])
            isOthers = False
            if 'time' in milestone['name'] or \
               'Time' in milestone['name'] or \
               'OWNER' in milestone['name']:
                isOthers = True
            if isALL:
                isOthers = False

            isArrival = True
            startDate = milestone['startDate']
            if not isALL and startDate is not None:
                startDateTime = parser.parse(startDate)
                if startDateTime > UTC_TODAY:
                    isArrival = False
                    print('対象外')

            if milestone['archived'] is False and not isOthers and isArrival:
                key = milestone['id']
                val = milestone['name']
                resp.update({key: val})
                print('対象')

        return resp

    # カテゴリ取得
    def getCategory(self, projectId):
        dataSender = DataSender()
        msParam = [
            ('apiKey', BACKLOG_API_KEY)
        ]
        CATEGORY_URL = '/api/v2/projects/' + projectId + '/categories'
        categoryList = dataSender.sendDataToBacklog(msParam, CATEGORY_URL)

        resp = {}
        for category in categoryList:
            key = category['id']
            val = category['name']
            resp.update({key: val})

        return resp
