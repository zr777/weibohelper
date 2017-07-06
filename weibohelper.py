# pyinstaller weibohelper.py --onefile
from bs4 import BeautifulSoup
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print('请输入cookie:')
cookie = input()

print('请输入uid:')
uid = input()
uids = (uid, )

headers = {
    "Cookies": cookie,
    "User-Agent":'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
}
r = requests.session()
r.headers.update(headers)


def get_comments_from_one_weibo(id):
    try:
        json = r.get(
            ('https://m.weibo.cn/api/comments/show?'
             'id={0}&page=1').format(id),
            verify=False,
        ).json()
        if json['ok'] == 1:
            comments = []
            for c in json['data']:
                comments.append(BeautifulSoup(c['text'], 'lxml').text)
                comments.append(c['user']['screen_name'])
            comments.reverse()
            return comments
        else:
            return ()
    except:
        return ()
    


def get_single_user_fisrt_weibo(uid):
    page_num = 1
    nickname = None
    weibo = None
    try:
        json = r.get(
            ('https://m.weibo.cn/api/container/getIndex?'
            'is_search[]=0&'
            'visible[]=0&'
            'is_all[]=1&'
            'is_tag[]=0&'
            'profile_ftype[]=1&'
            'page={0}&'
            'jumpfrom=weibocom&'
            'sudaref=weibo.com&'
            'type=uid&'
            'value={1}&'
            'containerid=107603{1}').format(page_num, uid),
            verify=False,
        ).json()
    except:
        return None, None
    if json['ok'] == 0:
        print('sth wrong')
        return None, None
    else:
        for card in json['cards']:
            if card['card_type'] == 9:
                weibo = [
                    card['mblog']['created_at'],
                    BeautifulSoup(
                        card['mblog']['text'], 'lxml'
                    ).text.replace(' \u200b\u200b\u200b', ''),
                    *get_comments_from_one_weibo(
                        card['mblog']['id']),
                ]

                nickname = card['mblog']['user']['screen_name'] + ' '
                
                break # 取第一个即可
    print('success for', nickname, ' - time', time.ctime())
    return nickname, weibo


import itchat
itchat.auto_login()
# 以小号登录形式，要先找到大号的账户
# username = itchat.search_friends(name='xx')[0]['UserName']
username = 'filehelper'

import json
from collections import defaultdict
records = defaultdict(lambda : (None, None))
while 1:
    for uid in uids:
        nickname, weibo = get_single_user_fisrt_weibo(uid)
        
        try_times = 5
        while nickname == None:
            nickname, weibo = get_single_user_fisrt_weibo(uid)
            try_times -= 1
            if try_times == 0:
                break
        if try_times == 0:
            continue

        if records[nickname][1:] != weibo[1:]:
            # print('发现新微博：', weibo)
            itchat.send(
                '\n---\n'.join((nickname, *weibo)),
                toUserName=username)
            records[nickname] = weibo
            
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False)
        else:
            print('没有新消息', time.ctime())
            pass
    time.sleep(120)
