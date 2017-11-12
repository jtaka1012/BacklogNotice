# encoding: utf-8
import os
from pytz import timezone
from datetime import datetime
from datetime import timedelta
from datasender import DataSender
from backlogCommon import BacklogCommon


tzJst = timezone("Asia/Tokyo")
NOW = datetime.now(timezone('Asia/Tokyo'))
UTC_TODAY = datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0, tzinfo=tzJst)
TOMORROW = NOW + timedelta(days=1)
UTC_TODAY_FOR_UNTIL = datetime(TOMORROW.year, TOMORROW.month, TOMORROW.day, 0, 0, 0, tzinfo=tzJst)

# FOOD, TTO
PROJECT_LIST = [('4464', 'BACKLOG_NOTICE')]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]


def shortMeeting():

    # 曜日判定
    weekDay = UTC_TODAY.weekday()
    if weekDay == 5 or weekDay == 6:
        print("休日のため出力なし")
        return

    # STATUS ID
    NOT_START_YET = '1'  # 未対応
    STARTED = '2'  # 処理中

    ISSUE_URL = '/api/v2/issues'

    # 共通パラメータ作成
    commonParam = [
        ('apiKey', os.environ["BACKLOG_API_KEY"]),
        ("sort", 'assignee'),
        ('count', 100)
    ]

    dataSender = DataSender()

    # タイトル通知
    text = ':tada: ' + '*' + UTC_TODAY.strftime("%Y-%m-%d") + 'のタスク状況です' + '*' + ' :tada:'
    dataSender.sendDataToSlack(text, SLACK_CHANNEL)

    for projectDataSet in PROJECT_LIST:

        projectId = projectDataSet[0]
        projectTitle = projectDataSet[1]

        projectParam = [("projectId[]", projectId)]
        backlogCommon = BacklogCommon()
        milestones = backlogCommon.getMileStones(projectId, UTC_TODAY, False)

        dataSender.sendDataToSlack('*' + projectTitle + '*', SLACK_CHANNEL)

        # ここでマイルストーンでループ、テキストを結合して送信
        for milestone, milestoneTitle in milestones.items():
            text = ''
            milestone = [('milestoneId[]', milestone)]

            # 時期未設定
            # 一覧を取得し、startDateがnull or dueDateがnullのものを取得する
            tbdParam = [
                ('statusId[]', NOT_START_YET),
                ('statusId[]', STARTED)
            ]

            param = commonParam + milestone + projectParam + tbdParam
            resp = dataSender.sendDataToBacklog(param, ISSUE_URL)
            if len(resp) > 0:
                text = createNoticeTextForTBD(resp, '■ 期限未設定')

            # 期限が到来していて、未着手の案件
            notStartYetParam = [
                ("startDateUntil", UTC_TODAY_FOR_UNTIL.strftime("%Y-%m-%d")),
                ('statusId[]', NOT_START_YET)
            ]
            param = commonParam + notStartYetParam + milestone + projectParam
            resp = dataSender.sendDataToBacklog(param, ISSUE_URL)
            if len(resp) > 0:
                text = createNoticeText(resp, '■ 未着手')

            # text = text + '\n' + createNoticeText(resp, '_未着手_')

            # 着手中の案件
            startedParam = [
                ('dueDateSince', UTC_TODAY.strftime("%Y-%m-%d")),
                ('statusId[]', STARTED)
            ]
            param = commonParam + startedParam + milestone + projectParam
            resp = dataSender.sendDataToBacklog(param, ISSUE_URL)
            if len(resp) > 0:
                ct = createNoticeText(resp, '■ 着手中')
                text = ct if len(text) == 0 else text + '\n\n' + ct

            # 期限切れタスク
            expiredParam = [
                ('dueDateUntil', UTC_TODAY.strftime("%Y-%m-%d")),
                ('statusId[]', STARTED)
            ]
            param = commonParam + expiredParam + milestone + projectParam
            resp = dataSender.sendDataToBacklog(param, ISSUE_URL)
            if len(resp) > 0:
                ct = createNoticeText(resp, '■ 期限切れ')
                text = ct if len(text) == 0 else text + '\n\n' + ct

            # Slackへの通知
            if len(text) > 0:
                title = '\n\n>マイルストーン ' + milestoneTitle + '\n'
                text = title + '```\n' + text + '\n```'
                dataSender.sendDataToSlack(text, SLACK_CHANNEL)


# 通知用テキストの生成
def createNoticeText(issueList: list, status: str) -> str:

    assigneeIssues = {}
    for issue in issueList:
        isUserSet = True if issue['assignee'] is not None else False
        # 担当者判定
        if isUserSet:
            assigneeId = str(issue['assignee']['id'])
        else:
            assigneeId = 'nouser'

        # 通知に使う課題要素
        issueDict = {
            "status": status,
            "name": issue['assignee']['name'] if isUserSet else '担当割当なし',
            "title": issue['summary'],
            "issueKey": issue['issueKey'],
            "due": issue['dueDate']
        }

        assigneeIssues = setIssueGroupByUser(assigneeIssues, assigneeId, issueDict)

    text = createNoticeTextGroupByUser(assigneeIssues, status)
    return text


# 時期未定用テキスト生成
def createNoticeTextForTBD(issueList: list, status: str) -> str:

    assigneeIssues = {}
    for issue in issueList:

        # 時期未設定判定
        startDate = issue['startDate']
        dueDate = issue['dueDate']

        if startDate is None and dueDate is None:
            continue

        if startDate is None or dueDate is None:
            # 担当者判定
            isUserSet = True if issue['assignee'] is not None else False
            if isUserSet:
                assigneeId = str(issue['assignee']['id'])
            else:
                assigneeId = 'nouser'

            # 通知に使う課題要素
            issueDict = {
                "status": status,
                "name": issue['assignee']['name'] if isUserSet else '担当割当なし',
                "title": issue['summary'],
                "issueKey": issue['issueKey'],
                "due": '期限未設定'
            }

            assigneeIssues = setIssueGroupByUser(assigneeIssues, assigneeId, issueDict)

    if len(assigneeIssues) == 0:
        return ""
    else:
        text = createNoticeTextGroupByUser(assigneeIssues, status)
        return text


# 担当者別課題設定
def setIssueGroupByUser(assigneeIssues: dict, assigneeId: str, issueDict: dict) -> dict:
        userIssueList = []
        # すでに該当ユーザーの課題が通過済みかどうかを確認
        if assigneeId in assigneeIssues:
            userIssueList = assigneeIssues[assigneeId]
            userIssueList.append(issueDict)
        else:
            userIssueList.append(issueDict)

        # 課題要素を追加
        assigneeIssues.update({str(assigneeId): userIssueList})

        return assigneeIssues


# ユーザー毎に並べ替えした通知用のテキストを生成
def createNoticeTextGroupByUser(assigneeIssues: dict, status: str) -> str:
    # ユーザー毎にDictionary化された課題をテキストにまとめ直す
    respText = ''
    for key, issueList in assigneeIssues.items():
        user = '□ ' + issueList[0]['name']
        respText = user if len(respText) == 0 else respText + '\n\n' + user

        for issue in issueList:
            if issue['due'] is None:
                dueDate = '期限未設定'
            else:
                dueDate = issue['due'][0:10]  # 期限
            issueTitle = issue['title']  # タイトル
            issueKey = issue['issueKey']
            respText = respText + '\n' + dueDate + ": " + issueKey + ' ' + issueTitle

    return status + '\n' + respText


if __name__ == '__main__':
    shortMeeting()
