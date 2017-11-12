# encoding: utf-8
import os
from pytz import timezone
from datetime import datetime
from datetime import timedelta
from backlogCommon import BacklogCommon
from datasender import DataSender


NOW = datetime.now(timezone('Asia/Tokyo'))
tzJst = timezone("Asia/Tokyo")
UTC_TODAY = datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0, tzinfo=tzJst)

# プロジェクトと対象の種別
PROJECT_LIST = [('4464', 'Backlog_Notice', ['19509', '19508'])]


# プロダクトマッピング
PRODUCT_MAP = [
    ('iPhoneApp', [('4464', '6094')]),
    ('AndroidApp', [('4464', '6095')]),
    ('Web', [('4464', '6096')]),
]


BACKLOG_API_KEY = os.environ["BACKLOG_API_KEY"]
PERCOUNT = 50
SLACK_CHANNEL_CONTACT = os.environ["SLACK_CHANNEL_CONTACT"]


class CategoryDetail:

    def __init__(self, projectId, projectName, categoryId, categoryName, date):
        self.projectId = str(projectId)
        self.projectName = projectName
        self.categoryId = str(categoryId)
        self.categoryName = categoryName
        self.date = str(date)
        self.weekDay = 0
        self.count = 0
        self.contactTitles = []


# 問い合わせ集計
def contactSummary(fromDate, toDate, isOneDay):

    # タイトル
    if isOneDay:
        title = fromDate.strftime("%Y-%m-%d") + 'の問い合わせ件数'
    else:
        title = fromDate.strftime("%Y-%m-%d") + 'から' + toDate.strftime("%Y-%m-%d") + 'の問い合わせ件数'

    dataSender = DataSender()
    dataSender.sendDataToSlack(title, SLACK_CHANNEL_CONTACT)

    pjCategoryDetailList = []

    # 対象となるプロジェクト
    for projectSet in PROJECT_LIST:
        projectId = projectSet[0]
        projecName = projectSet[1]
        validIssueTypeList = projectSet[2]

        # カテゴリの一覧を取得
        backlogCommon = BacklogCommon()
        categoryList = backlogCommon.getCategory(projectId)

        # カテゴリ毎に１日の件数を集計する
        ISSUE_URL = '/api/v2/issues'
        COUNT_URL = '/api/v2/issues/count'

        # toDateをUntil用に１日加算する
        toDateForUntil = toDate + timedelta(days=1)

        # 共通パラメータ作成
        commonParam = [
            ('apiKey', BACKLOG_API_KEY),
            ('createdSince', fromDate.strftime("%Y-%m-%d")),
            ('createdUntil', toDateForUntil.strftime("%Y-%m-%d"))
        ]

        for categoryKey, categoryVal in categoryList.items():

            categoryId = categoryKey

            # プロジェクトのすべての課題を抽出する
            issueParam = [
                ("projectId[]", projectId),
                ("categoryId[]", categoryId),
                ('sort', 'created'),
                ('order', 'asc')
            ]

            param = commonParam + issueParam
            respDict = dataSender.sendDataToBacklog(param, COUNT_URL)
            count = respDict['count']

            dmResult = divmod(count, PERCOUNT)
            roopEnd = dmResult[0]
            if dmResult[1] != 0:
                roopEnd += 1

            categoryDetailList = []
            for i in range(0, roopEnd):

                countParam = [
                    ('count', PERCOUNT),
                    ('offset', i*PERCOUNT)
                ]

                cp = param + countParam
                issueList = dataSender.sendDataToBacklog(cp, ISSUE_URL)

                for issue in issueList:

                    # 対象の種別かを確認
                    issueTypeId = str(issue['issueType']['id'])
                    issueStatus = issue['status']['id']

                    if issueTypeId not in validIssueTypeList:
                        continue

                    # 日付
                    # すでにデータがあるかを確認
                    cd = getCategoryDetail(categoryDetailList, issue)
                    if cd is None:
                        date = datetime.strptime(issue['created'], '%Y-%m-%dT%H:%M:%SZ')
                        # createDate = str(date.year) + str(date.month) + str(date.day)

                        strDate = issue['created']
                        strCD = strDate[0:4] + strDate[5:7] + strDate[8:10]

                        tzJst = timezone("Asia/Tokyo")
                        dtcd = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tzJst)
                        wd = dtcd.weekday()

                        cd = CategoryDetail(projectId, projecName, categoryKey, categoryVal, strCD)

                        cd.weekDay = wd
                        categoryDetailList.append(cd)

                    # 件数を追加
                    cd.count = cd.count + 1

                    if isOneDay:
                        if issueStatus == 1 or issueStatus == 2:
                            statusMark = '□'
                        else:
                            statusMark = '■'

                        title = "{:<18}".format(issue['issueKey']) + ' ' + issue['summary']
                        cd.contactTitles.append(statusMark + ' ' + title)

            for cd in categoryDetailList:
                pjCategoryDetailList.append(cd)

            text = ''
            for cd in categoryDetailList:
                if len(text) > 0:
                    text = text + '\n\n'

                if isOneDay:
                    text = text + "{:<15}".format(cd.categoryName) + ' 件数: ' + str(cd.count)
                    for title in cd.contactTitles:
                        text = text + '\n' + title
                else:
                    date = str(cd.date)[0:4] + '/' + str(cd.date)[4:6] + '/' + str(cd.date)[6:8]
                    text = text + date + ' ' + "{:<25}".format(cd.projectName + ': ' + cd.categoryName) + ' 件数: ' + str(cd.count)

            if isOneDay and len(text) > 0:
                pjTitle = '>' + cd.projectName + '\n'
                text = pjTitle + '```\n' + text + '\n```'
                dataSender.sendDataToSlack(text, SLACK_CHANNEL_CONTACT)

    # 集計
    if not isOneDay:
        summaryDict = {}
        for cd in pjCategoryDetailList:
            for pmd in PRODUCT_MAP:
                isFound = False

                productName = pmd[0]
                productMapList = pmd[1]
                for pm in productMapList:
                    if pm[0] == cd.projectId and pm[1] == cd.categoryId:
                        if productName in summaryDict:
                            count = summaryDict[productName]
                            count = count + cd.count
                            summaryDict[productName] = count
                        else:
                            summaryDict[productName] = cd.count

                        isFound = True
                    continue

                if isFound:
                    continue

        titleText = '>集計結果' + '\n'
        text = ''
        for key, value in summaryDict.items():
            if len(text) > 0:
                text = text + '\n'
            text = text + "{:<25}".format(key + ': ') + str(value)

        text = titleText + '```\n' + text + '\n```'
        dataSender.sendDataToSlack(text, SLACK_CHANNEL_CONTACT)

def getCategoryDetail(list, issue):
    for cd in list:
        strDate = issue['created']
        createDate = strDate[0:4] + strDate[5:7] + strDate[8:10]

        if cd.projectId == str(issue['projectId']) and \
           cd.categoryId == str(issue['category'][0]['id']) and \
           cd.date == createDate:
            return cd

    return None


if __name__ == '__main__':

    fromDate = datetime(NOW.year, NOW.month, NOW.day-1, 0, 0, 0, tzinfo=tzJst)
    toDate = datetime(NOW.year, NOW.month, NOW.day-1, 0, 0, 0, tzinfo=tzJst)

    contactSummary(fromDate, toDate, True)
