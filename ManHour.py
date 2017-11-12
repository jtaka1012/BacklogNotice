# encoding: utf-8
import os
import calendar
from pytz import timezone
from datetime import datetime
from datetime import timedelta
from backlogCommon import BacklogCommon
from datasender import DataSender
from typing import List
import csv


NOW = datetime.now(timezone('Asia/Tokyo'))
tzJst = timezone("Asia/Tokyo")
UTC_TODAY = datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0, tzinfo=tzJst)

# FOOD, TTO
PROJECT_LIST = [('4464', 'BACKLOG_NOTICE')]

# ENV_PARAM
BACKLOG_API_KEY = os.environ["BACKLOG_API_KEY"]
SLACK_CHANNEL_MANAGE = os.environ["SLACK_CHANNEL_MANAGE"]
PERCOUNT = 50


# 作業時間用クラス
class ManHours:
    def __init__(self, userId, userName):
        self.userId = userId
        self.userName = userName
        self.weeklyEstimatedHours = 0.00
        self.weeklyActualHours = 0.00
        self.nextWeeklyEstimatedHours = 0.00
        self.nextWeeklyActualHours = 0.00
        self.monthlyEstimatedHours = 0.00
        self.monthlyActualHours = 0.00
        self.nextMonthlyEstimatedHours = 0.00
        self.nextMonthlyActualHours = 0.00
        self.projectId = ""
        self.projectName = ""
        self.milestoneId = ""
        self.milestoneName = ""

    def getWeeklyEstimatedHours(self):
        return float("{0:.2f}".format(float(self.weeklyEstimatedHours)))

    def getWeeklyActualHours(self):
        return float("{0:.2f}".format(float(self.weeklyActualHours)))

    def getNextWeeklyEstimatedHours(self):
        return float("{0:.2f}".format(float(self.nextWeeklyEstimatedHours)))

    def getNextWeeklyActualHours(self):
        return float("{0:.2f}".format(float(self.nextWeeklyActualHours)))

    def getMonthlyEstimatedHours(self):
        return float("{0:.2f}".format(float(self.monthlyEstimatedHours)))

    def getMonthlyActualHours(self):
        return float("{0:.2f}".format(float(self.monthlyActualHours)))

    def getNextMonthlyEstimatedHours(self):
        return float("{0:.2f}".format(float(self.nextMonthlyEstimatedHours)))

    def getNextMonthlyActualHours(self):
        return float("{0:.2f}".format(float(self.nextMonthlyActualHours)))

    def exportForCSV(self):
        return [self.userId,
                self.userName,
                self.getWeeklyEstimatedHours(),
                self.getWeeklyActualHours(),
                self.getNextWeeklyEstimatedHours(),
                self.getNextWeeklyActualHours(),
                self.getMonthlyEstimatedHours(),
                self.getMonthlyActualHours(),
                self.getNextMonthlyEstimatedHours(),
                self.getNextMonthlyActualHours()]


# 個人トータル集計用クラス
class PersonalManHours:
    def __init__(self, userId, userName):
        self.userId = userId
        self.userName = userName
        self.manHoursList = []

    def totalWeeklyEstimatedHours(self):
        weh = 0.00
        for wh in self.manHoursList:
            weh = weh + wh.weeklyEstimatedHours
        return float("{0:.2f}".format(float(weh)))

    def totalWeeklyActualHours(self):
        wah = 0.00
        for wh in self.manHoursList:
            wah = wah + wh.weeklyActualHours
        return float("{0:.2f}".format(float(wah)))

    def totalNextWeeklyEstimatedHours(self):
        weh = 0.00
        for wh in self.manHoursList:
            weh = weh + wh.nextWeeklyEstimatedHours
        return float("{0:.2f}".format(float(weh)))

    def totalNextWeeklyActualHours(self):
        wah = 0.00
        for wh in self.manHoursList:
            wah = wah + wh.nextWeeklyActualHours
        return float("{0:.2f}".format(float(wah)))

    def totalMonthlyEstimatedHours(self):
        meh = 0.00
        for wh in self.manHoursList:
            meh = meh + wh.monthlyEstimatedHours
        return float("{0:.2f}".format(float(meh)))

    def totalMonthlyActualHours(self):
        mah = 0.00
        for wh in self.manHoursList:
            mah = mah = wh.monthlyActualHours
        return float("{0:.2f}".format(float(mah)))

    def totalNextMonthlyEstimatedHours(self):
        nmeh = 0.00
        for wh in self.manHoursList:
            nmeh = nmeh + wh.nextMonthlyEstimatedHours
        return float("{0:.2f}".format(float(nmeh)))

    def totalNextMonthlyActualHours(self):
        nmah = 0.00
        for wh in self.manHoursList:
            nmah = nmah = wh.nextMonthlyActualHours
        return float("{0:.2f}".format(float(nmah)))

    def exportForCSV(self):
        return [self.userId,
                self.userName,
                self.totalWeeklyEstimatedHours(),
                self.totalWeeklyActualHours(),
                self.totalNextWeeklyEstimatedHours(),
                self.totalNextWeeklyActualHours(),
                self.totalMonthlyEstimatedHours(),
                self.totalMonthlyActualHours(),
                self.totalNextMonthlyEstimatedHours(),
                self.totalNextMonthlyActualHours()]


# 予実集計
def getManHours():

    # 曜日判定
    weekDay = UTC_TODAY.weekday()
    if weekDay == 5 or weekDay == 6:
        print("休日のため出力なし")
        return

    # １ヶ月分の課題を取得
    dataSender = DataSender()

    COUNT_URL = '/api/v2/issues/count'
    ISSUE_URL = '/api/v2/issues'

    # 共通パラメータ作成
    commonParam = [
        ('apiKey', BACKLOG_API_KEY)
    ]

    manHourList = []

    for projectDataSet in PROJECT_LIST:

        projectId = projectDataSet[0]
        projectName = projectDataSet[1]

        backlogCommon = BacklogCommon()
        milestones = backlogCommon.getMileStones(projectId, UTC_TODAY, True)

        # プロジェクトのすべての課題を抽出する
        issueParam = [
            ("projectId[]", projectId),
        ]

        # マイルストーン毎にすべてのissueをひろう
        for milestone, milestoneTitle in milestones.items():

            milestone = [('milestoneId[]', milestone)]

            param = commonParam + issueParam + milestone

            # 件数の取得
            respDict = dataSender.sendDataToBacklog(param, COUNT_URL)
            count = respDict['count']

            dmResult = divmod(count, PERCOUNT)
            roopEnd = dmResult[0]
            if dmResult[1] != 0:
                roopEnd += 1

            print('msTitle: ' + milestoneTitle + 'count: ' + str(count) + ' roopEnd: ' + str(roopEnd))

            for i in range(0, roopEnd):
                # 共通パラメータ作成
                countParam = [
                    ('count', PERCOUNT),
                    ('offset', i*PERCOUNT),
                    ("sort", 'assignee')
                ]

                print('offset: ' + str(i*PERCOUNT))

                cp = param + countParam

                issueList = dataSender.sendDataToBacklog(cp, ISSUE_URL)

                print('issueListCount: ' + str(len(issueList)))
                # 作業時期が確定しているタスク
                for issue in issueList:
                    # print(issue)

                    # 開始日、終了日を取得
                    startDate = issue['startDate']
                    dueDate = issue['dueDate']

                    if startDate is not None and dueDate is not None:
                        # 予定時間クラスの生成有無確認
                        mh: ManHours = getManHour(issue, manHourList)
                        isFirstMH = False
                        if mh is None:
                            # クラスを作って、人別で1週間分の作業量、実績、 一ヶ月分の作業量、実績を集計していく
                            userSet = getUserSet(issue)
                            milestoneSet = getMileStoneSet(issue)
                            userId = userSet[0]
                            userName = userSet[1]
                            milestoneId = milestoneSet[0]
                            milestoneName = milestoneSet[1]
                            projectId = projectDataSet[0]
                            projectName = projectDataSet[1]

                            mh = ManHours(userId, userName)
                            mh.projectId = projectId
                            mh.projectName = projectName
                            mh.milestoneId = milestoneId
                            mh.milestoneName = milestoneName
                            mh.projectId = projectId
                            mh.projectName = projectName
                            isFirstMH = True

                        # 今週の工数算出
                        thisWeekDays = getThisWeekDaySet(UTC_TODAY)
                        startDay = thisWeekDays[0]
                        endDay = thisWeekDays[1]
                        thisWeekEstimatedHour = getEstimatedManHour(startDay, endDay, issue)
                        mh.weeklyEstimatedHours += thisWeekEstimatedHour
                        thisWeekActualHour = getActualManHour(startDay, endDay, issue)
                        mh.weeklyActualHours += thisWeekActualHour

                        # 来週の工数算出
                        nextWeekDays = getNextWeekDaySet(UTC_TODAY)
                        startDay = nextWeekDays[0]
                        endDay = nextWeekDays[1]
                        nextWeekEstimatedHour = getEstimatedManHour(startDay, endDay, issue)
                        mh.nextWeeklyEstimatedHours += nextWeekEstimatedHour
                        nextWeekActualHour = getActualManHour(startDay, endDay, issue)
                        mh.nextWeeklyActualHours += nextWeekActualHour

                        # 今月の工数算出
                        thisMonthDays = getThisMonthDaySet(UTC_TODAY)
                        startDay = thisMonthDays[0]
                        endDay = thisMonthDays[1]
                        thisMonthEstimatedHour = getEstimatedManHour(startDay, endDay, issue)
                        mh.monthlyEstimatedHours += thisMonthEstimatedHour
                        thisMonthActualHour = getActualManHour(startDay, endDay, issue)
                        mh.monthlyActualHours += thisMonthActualHour

                        # 翌月の工数算出
                        nextMonthDays = getNextMonthDaySet(UTC_TODAY)
                        startDay = nextMonthDays[0]
                        endDay = nextMonthDays[1]
                        nextMonthEstimatedHour = getEstimatedManHour(startDay, endDay, issue)
                        mh.nextMonthlyEstimatedHours += nextMonthEstimatedHour
                        nextMonthActualHour = getActualManHour(startDay, endDay, issue)
                        mh.nextMonthlyActualHours += nextMonthActualHour

                        if isFirstMH:
                            manHourList.append(mh)

    # 人別でトータルの工数を集計する
    pmhl: List[PersonalManHours] = getUserTotalManHour(manHourList)

    # 出力
    mhText = ''
    for pmh in pmhl:
        # total
        if pmh.totalWeeklyEstimatedHours() != 0.00 or \
           pmh.totalMonthlyEstimatedHours() != 0.00 or \
           pmh.totalMonthlyEstimatedHours() != 0.00:

            # サマリ情報をText送信
            if len(mhText) > 0:
                mhText = mhText + '\n\n'

            mhText = mhText + pmh.userName + '\n'
            spaceStr = getSpaceStr(len(str(pmh.totalWeeklyEstimatedHours())), 6)
            mhText = mhText + '今週見積: ' + str(pmh.totalWeeklyEstimatedHours()) + spaceStr + '  '

            spaceStr = getSpaceStr(len(str(pmh.totalWeeklyActualHours())), 6)
            mhText = mhText + '今週実績: ' + str(pmh.totalWeeklyActualHours()) + spaceStr + '  '

            spaceStr = getSpaceStr(len(str(pmh.totalNextWeeklyEstimatedHours())), 6)
            mhText = mhText + '来週見積: ' + str(pmh.totalNextWeeklyEstimatedHours()) + spaceStr + '  '

            # spaceStr = getSpaceStr(len(str(pmh.totalNextWeeklyActualHours())), 6)
            # mhText = mhText + '来週実績: ' + str(pmh.totalNextWeeklyActualHours()) + spaceStr + '  '

            spaceStr = getSpaceStr(len(str(pmh.totalMonthlyEstimatedHours())), 6)
            mhText = mhText + '今月見積: ' + str(pmh.totalMonthlyEstimatedHours()) + spaceStr + '  '

            spaceStr = getSpaceStr(len(str(pmh.totalMonthlyActualHours())), 6)
            mhText = mhText + '今月実績: ' + str(pmh.totalMonthlyActualHours()) + spaceStr + '  '

            spaceStr = getSpaceStr(len(str(pmh.totalNextMonthlyEstimatedHours())), 6)
            mhText = mhText + '来月見積: ' + str(pmh.totalNextMonthlyEstimatedHours()) + spaceStr + '  '

            # spaceStr = getSpaceStr(len(str(pmh.totalNextMonthlyActualHours())), 6)
            # mhText = mhText + '来月実績: ' + str(pmh.totalNextMonthlyActualHours())

    if len(mhText) > 0:
        title = '*' + UTC_TODAY.strftime("%Y-%m-%d") + 'の工数状況' + '*'
        postText = '```\n' + mhText + '\n```'
        dataSender.sendDataToSlack(title, SLACK_CHANNEL_MANAGE)
        dataSender.sendDataToSlack(postText, SLACK_CHANNEL_MANAGE)

    # CSV出力
    # 金曜日のみ実施
    if weekDay == 4:
        if os.path.isfile('manHour.csv'):
            os.remove('manHour.csv')
        with open('manHour.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')  # writerオブジェクトを作成
            titleList = [
                "担当者",
                "プロジェクト",
                "マイルストーン",
                "今週予定時間",
                "今週実績時間",
                "来週予定時間",
                "来週実績時間",
                "月間予定時間",
                "月間実績時間",
                "翌月予定時間",
                "翌月実績時間"
            ]
            writer.writerow(titleList)

            for pmh in pmhl:
                writer.writerow(pmh.exportForCSV())
                for mh in pmh.manHoursList:
                    writer.writerow(mh.exportForCSV())

        with open('manHour.csv', 'r', encoding='utf-8') as f:
            # slackへ送信
            title = UTC_TODAY.strftime("%Y-%m-%d") + 'の工数状況'
            filename = 'manhour' + UTC_TODAY.strftime("%Y%m%d")
            dataSender.sendDataToSlackWithFile(title, filename, 'csv', f, SLACK_CHANNEL_MANAGE)


# ユーザー取得
def getUserSet(issue: dict) -> (str):
    # 担当者判定
    isUserSetted = True if issue['assignee'] is not None else False
    if isUserSetted:
        userId = str(issue['assignee']['id'])
        userName = str(issue['assignee']['name'])
        return (userId, userName)
    else:
        return ('nouser', '担当割当なし')


# マイルストーン取得
def getMileStoneSet(issue: dict) -> (str):
    if issue['milestone'] is not None and len(issue['milestone']) > 0:
        milestoneId = str(issue['milestone'][0]['id'])
        milestoneName = str(issue['milestone'][0]['name'])
        return (milestoneId, milestoneName)
    else:
        return ('unset', 'マイルストーン未設定')


# 作業時間クラス保持判定
def getManHour(issue: dict, mhList: list):
    assigneeId = getUserSet(issue)[0]
    projectId = str(issue["projectId"])
    milestoneId = getMileStoneSet(issue)[0]
    # print('assigneeId: ' + assigneeId + ' projectId: ' + projectId + ' milestoneId: ' + milestoneId)

    for mh in mhList:
        if mh.userId == assigneeId and \
         mh.projectId == projectId and \
         mh.milestoneId == milestoneId:
            return mh
    return None


# 作業時間算出用メソッド
def getEstimatedManHour(startDate: datetime, endDate: datetime, issue: dict) -> float:
    targetHour = issue['estimatedHours']
    if targetHour is None:
        return 0.00
    else:
        return calcManHour(startDate, endDate, issue, int(targetHour))


def getActualManHour(startDate: datetime, endDate: datetime, issue: dict) -> float:
    targetHour = issue['actualHours']
    if targetHour is None:
        return 0.00
    else:
        return calcManHour(startDate, endDate, issue, int(targetHour))


def calcManHour(startDate: datetime, endDate: datetime, issue: dict, targetHour: int) -> float:
    # 課題中のstartDay, endDayを取得
    isd = issue['startDate']
    idd = issue['dueDate']

    # バリデーションチェック
    if isd is None:
        return 0.00
    if idd is None:
        return 0.00

    # print('issue start: ' + isd + ' due: ' + idd + ' Target start: ' + startDate.strftime('%Y/%m/%d') + ' end: ' + endDate.strftime('%Y/%m/%d'))

    iSDD = datetime.strptime(isd, '%Y-%m-%dT%H:%M:%SZ')
    iDDD = datetime.strptime(idd, '%Y-%m-%dT%H:%M:%SZ')

    tzJst = timezone("Asia/Tokyo")
    issueStartDate = datetime(iSDD.year, iSDD.month, iSDD.day, 0, 0, 0, tzinfo=tzJst)
    issueDueDate = datetime(iDDD.year, iDDD.month, iDDD.day, 0, 0, 0, tzinfo=tzJst)

    # 対象外課題チェック
    # 対象範囲より前
    if (issueDueDate - startDate).days < 0:
        # print("範囲前")
        return 0.00
    # 対象範囲より後
    if (issueStartDate - endDate).days > 0:
        # print("範囲後")
        return 0.00

    # startより前の日数算出
    diffDay = 0
    startDiffDay = (startDate - issueStartDate).days
    if startDiffDay > 0:
        diffDay = startDiffDay

    # endより後ろの日数算出
    endDiffDay = (issueDueDate - endDate).days
    if endDiffDay > 0:
        diffDay = diffDay + endDiffDay

    # 全体から対象外期間の日数を引く
    totalDay = (issueDueDate - issueStartDate).days
    workDay = totalDay - diffDay

    if workDay < 0:
        # print('totalDay: ' + str(totalDay) + ' diffDay: ' + str(diffDay) + ' workDay: ' + str(workDay) + ' startDiff: ' + str(startDiffDay) + ' endDiff: ' + str(endDiffDay))
        return 0.00

    if totalDay == 0:
        workDayPer = 1
    else:
        # 対象期間のパーセンテージを算出
        workDayPer = workDay / totalDay

    # 工数算出(小数点２桁まで)
    hour = float("{0:.2f}".format(float(targetHour) * float(workDayPer)))

    # print("title: " + issue['summary'] + " workDayPer: " + str(workDayPer) + " hour: " + str(hour))

    return hour


# 今週のセット
def getThisWeekDaySet(today: datetime) -> (datetime):
    # 本日の曜日を取得
    todaysWeekDay = today.weekday()
    # 開始日 (月曜日)
    startDay = today - timedelta(todaysWeekDay)
    # 終了日 (日曜日)
    endDay = today + timedelta(6-todaysWeekDay)

    return (startDay, endDay)


# 来週のセット
def getNextWeekDaySet(today: datetime) -> (datetime):
    # 本日の曜日を取得
    todaysWeekDay = today.weekday()
    # 開始日 (月曜日)
    startDay = today - timedelta(todaysWeekDay) + timedelta(days=7)
    # 終了日 (日曜日)
    endDay = today + timedelta(6-todaysWeekDay) + timedelta(days=7)

    return (startDay, endDay)


# 今月のセット
def getThisMonthDaySet(today: datetime) -> (datetime):
    tzJst = timezone("Asia/Tokyo")
    # 今月の日数を取得
    monthRange = calendar.monthrange(today.year, today.month)
    # 月初
    startDay = datetime(today.year, today.month, 1, 0, 0, 0, tzinfo=tzJst)
    # 月末
    endDay = datetime(today.year, today.month, monthRange[1], 0, 0, 0, tzinfo=tzJst)

    return (startDay, endDay)


# 翌月のセット
def getNextMonthDaySet(today: datetime) -> (datetime):
    tzJst = timezone("Asia/Tokyo")

    year = today.year
    month = today.month

    # 来月を取得
    if today.month == 12:
        year = year + 1
        month = 1
    else:
        month = month + 1

    # 今月の日数を取得
    monthRange = calendar.monthrange(year, month)
    # 月初
    startDay = datetime(year, month, 1, 0, 0, 0, tzinfo=tzJst)
    # 月末
    endDay = datetime(year, month, monthRange[1], 0, 0, 0, tzinfo=tzJst)

    return (startDay, endDay)


# ユーザー毎の工数を集計する
def getUserTotalManHour(mhList: list):
    respMHList = []
    for mh in mhList:
        # PersonalManHoursの取得
        pmh = getPersonalManHours(respMHList, mh)
        if pmh is None:
            pmh = PersonalManHours(mh.userId, mh.userName)
            respMHList.append(pmh)

        pmh.manHoursList.append(mh)

    return respMHList


# 文字レイアウト調整
def getSpaceStr(length, maxLength):
    if length >= maxLength:
        return ''
    else:
        count = maxLength - length
        spaceStr = ''
        for var in range(0, count):
            spaceStr = spaceStr + ' '
        return spaceStr


def getPersonalManHours(pMHL: List[PersonalManHours], mh: ManHours):
    for pmh in pMHL:
        if pmh.userId == mh.userId:
            return pmh
    return None


if __name__ == '__main__':
    getManHours()
