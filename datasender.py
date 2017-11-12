# encoding: utf-8
import os
import urllib.request
import json
import requests


BACKLOG_BASE_URL = os.environ["BACKLOG_BASE_URL"]
SLACK_API_KEY = os.environ["SLACK_API_KEY"]


class DataSender:

    # Backlogへ通信
    def sendDataToBacklog(self, params: list, endpoint: str) -> list:
        # urlの組み立て
        p = urllib.parse.urlencode(params)
        url = BACKLOG_BASE_URL + endpoint + "?" + p

        # アクセス
        with urllib.request.urlopen(url) as resp:
            content = json.loads(resp.read().decode('utf8'))
            return content

    # Slackへの通知
    def sendDataToSlack(self, text: str, channel):

        BASE_URL = 'https://slack.com/api/chat.postMessage'

        params = [
            ('token', SLACK_API_KEY),
            ('channel', channel),
            ('text', text),
            ('as_user', True)
        ]

        p = urllib.parse.urlencode(params)
        url = BASE_URL + '?' + p

        # アクセス
        with urllib.request.urlopen(url) as resp:
            content = json.loads(resp.read().decode('utf8'))
            return content

        # print(text)

    def sendDataToSlackWithFile(self, title, filename, fileType, file, channel):
        BASE_URL = 'https://slack.com/api/files.upload'

        params = {
            'token': SLACK_API_KEY,
            'channels': channel,
            'filename': filename,
            'title': title
        }

        # アクセス
        response = requests.post(BASE_URL, params=params, files={'file': file})
        return response
