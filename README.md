## Backlogツール    
### 概要  
Backlogでタスク管理をされている方向けの情報集計プログラムです。  
必要な情報をBacklogのAPIにて集計して、Slackへ通知します。  
  
### Backlog API  
https://developer.nulab-inc.com/ja/docs/backlog/  
  
### 利用システム前提  
- サーバ　　　： Heroku
- 言語　　　　： Python3.6.1
- Webサーバ　： Bottle Webサーバ
- ライブラリ　： Procfile参照してください
  
### プログラム構成  (主要部分)  
- backlogNotice.py (routeプログラム)
  - shortmeeting: 今日やることを出力  
  - manhour: 予定と実績のサマリ  
  - contactsummary: 問い合わせ実績出力  
    - 月曜日でには、先週１週間の件数サマリ情報が表示される   
- backlog.py (その日やることのまとめ)  
  - プロジェクト単位でグルーピング。さらにその中でマイルストーン毎にグルーピング  
  - 未着手、着手中、期限切れの3つに分類し、担当者毎にさらにグルーピング  
  - 担当者未設定の場合は `担当者なし` として表示  
  - 期限日: 課題名称 を一覧で表示  
  - 開始時期未設定かつ、期限未設定の場合は通知対象から除外。いずれかが設定されて入れば、時期未設定として通知対象となる  
- backlogCommon.py (マイルストーン取得、カテゴリ取得)  
  - マイルストーン取得時、開始日が設定かつ、本日よりも大きい場合は対象外(時期未到来)
  - マイルストーンがアーカイブではなく、未到来ではない場合。 
- ContactSummary.py (問い合わせ結果の集計)  
  - プロジェクトと対象種別: ヘッダーとして利用。(プロジェクトID,名称、有効なIssueType(種別))
  - プロダクトマッピング: プロダクトで、このプロジェクトIDとカテゴリIDとが結びつけられいる。 
- datasender.py (API Call)  
  - Backlogサーバへの通信、Slackへの通知を実施     
- ManHour.py (作業時間)  
  - 前提: タイムゾーンは `Asia/Tokyo`   
  - 今週見積、 今週実績、 来週見積、　今月見積、　今月実績、　来月見積 の順
  - 金曜日にCSVでレポート出力
  
### 利用にあたっての事前設定  
- 環境変数
  - SLACK_CHANNEL: 問い合わせ用Slackチャンネル名
  - BACKLOG_API_KEY: BacklogのApiKey
  - SLACK_CHANNEL_CONTACT: 問い合わせ用のSlackチャンネル名
  - BACKLOG_BASE_URL: Backlogのエンドポイント
  - SLACK_API_KEY: Slack用ApiKey
  - SLACK_CHANNEL_MANAGE: 管理用データを飛ばすのSlackチャンネル
- プログラム内定数
  注) 事前にAPI等で、BacklogのプロジェクトID、種別ID、カテゴリIDを取得しておいてください  
  - backlog.py
    - PROJECT_LIST [('PROJECT_ID', 'プロジェクト名')] 
  - contactSummary
    - PROJECT_LIST [('PROJECT_ID', 'プロジェクト名(タイトル用)', ['集計対象IssueType(種別)'])]  
    - PROJECT_MAP ['プロダクト名', [('PROJECT_ID', 'カテゴリID')]]
      - プロジェクトをまたいでプロダクトの問い合わせ集計が可能となる  
  - manHour
    - PROJECT_LIST [('PROJECT_ID', 'プロジェクト名')] 
    
## サンプルデータ  
### プロジェクト  
```
[
  {
    "id": 4464,
    "projectKey": "BACKLOG_NOTICE",
    "name": "Backlog_Notice",
    "chartEnabled": false,
    "subtaskingEnabled": false,
    "projectLeaderCanEditProjectLeader": false,
    "useWikiTreeView": true,
    "textFormattingRule": "markdown",
    "archived": false,
    "displayOrder": 2147483646
  }
]
```
  
### カテゴリー
```
[
  {
    "id": 6094,
    "name": "iPhoneApp",
    "displayOrder": 2147483646
  },
  {
    "id": 6095,
    "name": "AndroidApp",
    "displayOrder": 2147483646
  },
  {
    "id": 6096,
    "name": "Web",
    "displayOrder": 2147483646
  }
]
```
  
### 種別  
```
[
  {
    "id": 19509,
    "projectId": 4464,
    "name": "タスク",
    "color": "#7ea800",
    "displayOrder": 0
  },
  {
    "id": 19508,
    "projectId": 4464,
    "name": "バグ",
    "color": "#990000",
    "displayOrder": 1
  },
  {
    "id": 19510,
    "projectId": 4464,
    "name": "要望",
    "color": "#ff9200",
    "displayOrder": 2
  },
  {
    "id": 19511,
    "projectId": 4464,
    "name": "その他",
    "color": "#2779ca",
    "displayOrder": 3
  }
]
```
  
### 課題  
```
[
  {
    "id": 62763,
    "projectId": 4464,
    "issueKey": "BACKLOG_NOTICE-5",
    "keyId": 5,
    "issueType": {
      "id": 19508,
      "projectId": 4464,
      "name": "バグ",
      "color": "#990000",
      "displayOrder": 1
    },
    "summary": "問い合わせ１",
    "description": "といあわせ",
    "resolution": null,
    "priority": {
      "id": 3,
      "name": "中"
    },
    "status": {
      "id": 4,
      "name": "完了"
    },
    "assignee": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "category": [
      {
        "id": 6094,
        "name": "iPhoneApp",
        "displayOrder": 2147483646
      }
    ],
    "versions": [],
    "milestone": [],
    "startDate": null,
    "dueDate": "2017-11-11T00:00:00Z",
    "estimatedHours": null,
    "actualHours": null,
    "parentIssueId": null,
    "createdUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "created": "2017-11-12T03:38:32Z",
    "updatedUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "updated": "2017-11-12T03:42:36Z",
    "customFields": [],
    "attachments": [],
    "sharedFiles": [],
    "stars": []
  },
  {
    "id": 62692,
    "projectId": 4464,
    "issueKey": "BACKLOG_NOTICE-4",
    "keyId": 4,
    "issueType": {
      "id": 19509,
      "projectId": 4464,
      "name": "タスク",
      "color": "#7ea800",
      "displayOrder": 0
    },
    "summary": "課題４",
    "description": "課題４",
    "resolution": null,
    "priority": {
      "id": 3,
      "name": "中"
    },
    "status": {
      "id": 1,
      "name": "未対応"
    },
    "assignee": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "category": [
      {
        "id": 6094,
        "name": "iPhoneApp",
        "displayOrder": 2147483646
      }
    ],
    "versions": [
      {
        "id": 3247,
        "projectId": 4464,
        "name": "マイルストーン３",
        "description": "",
        "startDate": "2017-11-14T00:00:00Z",
        "releaseDueDate": "2017-11-20T00:00:00Z",
        "archived": false,
        "displayOrder": 2
      }
    ],
    "milestone": [
      {
        "id": 3247,
        "projectId": 4464,
        "name": "マイルストーン３",
        "description": "",
        "startDate": "2017-11-14T00:00:00Z",
        "releaseDueDate": "2017-11-20T00:00:00Z",
        "archived": false,
        "displayOrder": 2
      }
    ],
    "startDate": null,
    "dueDate": "2017-11-16T00:00:00Z",
    "estimatedHours": null,
    "actualHours": null,
    "parentIssueId": null,
    "createdUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "created": "2017-11-12T00:27:34Z",
    "updatedUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "updated": "2017-11-12T02:19:19Z",
    "customFields": [],
    "attachments": [],
    "sharedFiles": [],
    "stars": []
  },
  {
    "id": 62691,
    "projectId": 4464,
    "issueKey": "BACKLOG_NOTICE-3",
    "keyId": 3,
    "issueType": {
      "id": 19509,
      "projectId": 4464,
      "name": "タスク",
      "color": "#7ea800",
      "displayOrder": 0
    },
    "summary": "課題３",
    "description": "課題３",
    "resolution": null,
    "priority": {
      "id": 3,
      "name": "中"
    },
    "status": {
      "id": 2,
      "name": "処理中"
    },
    "assignee": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "category": [
      {
        "id": 6096,
        "name": "Web",
        "displayOrder": 2147483646
      }
    ],
    "versions": [],
    "milestone": [
      {
        "id": 3246,
        "projectId": 4464,
        "name": "マイルストーン２",
        "description": "",
        "startDate": "2017-11-07T00:00:00Z",
        "releaseDueDate": "2017-11-13T00:00:00Z",
        "archived": false,
        "displayOrder": 1
      }
    ],
    "startDate": null,
    "dueDate": "2017-11-13T00:00:00Z",
    "estimatedHours": null,
    "actualHours": null,
    "parentIssueId": null,
    "createdUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "created": "2017-11-12T00:26:10Z",
    "updatedUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "updated": "2017-11-12T02:19:08Z",
    "customFields": [],
    "attachments": [],
    "sharedFiles": [],
    "stars": []
  },
  {
    "id": 62690,
    "projectId": 4464,
    "issueKey": "BACKLOG_NOTICE-2",
    "keyId": 2,
    "issueType": {
      "id": 19509,
      "projectId": 4464,
      "name": "タスク",
      "color": "#7ea800",
      "displayOrder": 0
    },
    "summary": "課題2",
    "description": "課題2",
    "resolution": null,
    "priority": {
      "id": 3,
      "name": "中"
    },
    "status": {
      "id": 1,
      "name": "未対応"
    },
    "assignee": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "category": [
      {
        "id": 6095,
        "name": "AndroidApp",
        "displayOrder": 2147483646
      }
    ],
    "versions": [],
    "milestone": [
      {
        "id": 3246,
        "projectId": 4464,
        "name": "マイルストーン２",
        "description": "",
        "startDate": "2017-11-07T00:00:00Z",
        "releaseDueDate": "2017-11-13T00:00:00Z",
        "archived": false,
        "displayOrder": 1
      }
    ],
    "startDate": null,
    "dueDate": "2017-11-13T00:00:00Z",
    "estimatedHours": null,
    "actualHours": null,
    "parentIssueId": null,
    "createdUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "created": "2017-11-12T00:24:33Z",
    "updatedUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "updated": "2017-11-12T02:18:55Z",
    "customFields": [],
    "attachments": [],
    "sharedFiles": [],
    "stars": []
  },
  {
    "id": 62689,
    "projectId": 4464,
    "issueKey": "BACKLOG_NOTICE-1",
    "keyId": 1,
    "issueType": {
      "id": 19509,
      "projectId": 4464,
      "name": "タスク",
      "color": "#7ea800",
      "displayOrder": 0
    },
    "summary": "課題1",
    "description": "課題1",
    "resolution": null,
    "priority": {
      "id": 3,
      "name": "中"
    },
    "status": {
      "id": 2,
      "name": "処理中"
    },
    "assignee": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "category": [
      {
        "id": 6094,
        "name": "iPhoneApp",
        "displayOrder": 2147483646
      }
    ],
    "versions": [],
    "milestone": [
      {
        "id": 3245,
        "projectId": 4464,
        "name": "マイルストーン1",
        "description": "",
        "startDate": "2017-11-01T00:00:00Z",
        "releaseDueDate": "2017-11-06T00:00:00Z",
        "archived": false,
        "displayOrder": 0
      }
    ],
    "startDate": null,
    "dueDate": "2017-11-06T00:00:00Z",
    "estimatedHours": null,
    "actualHours": null,
    "parentIssueId": null,
    "createdUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "created": "2017-11-12T00:16:05Z",
    "updatedUser": {
      "id": 11760,
      "userId": "ydySh9GN2X",
      "name": "itaka",
      "roleType": 1,
      "lang": "ja",
      "mailAddress": "xxxx@gmail.com",
      "nulabAccount": {
        "nulabId": "tPRQ5adBHTzvqX6TmSNyO5jWzFuntapxH1NWI4oFtqMB6g8erX",
        "name": "Jun Takahashi",
        "uniqueId": "simplegadgetlife"
      }
    },
    "updated": "2017-11-12T02:18:44Z",
    "customFields": [],
    "attachments": [],
    "sharedFiles": [],
    "stars": []
  }
]
```

