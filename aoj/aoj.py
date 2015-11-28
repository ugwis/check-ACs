import websocket
import time
import json
import twitterkeys
import matplotlib.pyplot as plt
import numpy as np
import xmltodict
import urllib.request

from requests_oauthlib import OAuth1Session

checklist = ['ugwis','wanimaru','dyuma','iyselee','bgpat','toga2048']

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

def make_graph(filename,pid,rid,lang,cpu,mem,code):
    plt.clf()
    f = urllib.request.urlopen('http://judge.u-aizu.ac.jp/onlinejudge/webservice/solved_record?problem_id=' + str(pid))
    result = xmltodict.parse(f.read())
    cputime = []
    memory = []
    codesize = []
    for solved in result['solved_record_list']['solved']:
        print(solved)
        if solved['language'] == lang and solved['run_id'] != rid:
            cputime.append(int(solved['cputime'])*100)
            memory.append(int(solved['memory']))
            codesize.append(int(solved['code_size']))
    def subplt(pos,data,bins,x,xlabel):
        plt.subplot(pos)
        plt.hist(data,bins=bins,alpha=0.5)
        plt.yticks(list(map(int,np.linspace(plt.ylim()[0],plt.ylim()[1],3))))
        plt.axvline(x=x,linewidth=1,color='r')
        plt.xlabel(xlabel,size=14)
        plt.ylabel("Frequency",size=14)

    subplt(511,cputime,30,cpu*100,"CPU Time (ms)")

    subplt(513,codesize,30,code,"Code Size (Byte)")

    subplt(515,memory,30,mem,"Memory (KByte)")

    plt.savefig(filename)

def upload_image(filename):

    # OAuth認証 セッションを開始
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, twitterkeys.AT, twitterkeys.AS)

    # 画像投稿
    files = {"media" : open(filename, 'rb')}
    req_media = twitter.post(url_media, files = files)

    # レスポンスを確認
    if req_media.status_code != 200:
        print ("画像アップデート失敗: %s", req_media.text)
        exit()

    # Media ID を取得
    media_id = json.loads(req_media.text)['media_id']
    print ("Media ID: %d" % media_id)
    return media_id

def tweet(text,params):
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, twitterkeys.AT, twitterkeys.AS)
    req = twitter.post(url_text, params = params)
    return req.status_code

def on_message(ws,message):
    obj = json.loads(message)
    if obj['userID'] in checklist and obj['status'] == 4:
        problem = str(obj['problemID'])
        print(message)
        if obj['lessonID'] != "":
            problem = obj['lessonID'] + "_" + problem
        tweet_text = '[AOJ] ' + obj['userID'] + ' solved \'' + obj['problemTitle'] + '\' http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=' + problem
        make_graph("graph.png",problem,obj['runID'],obj['lang'],obj['cputime'],obj['memory'],obj['code'])
        media_id = upload_image("graph.png")
        status = tweet(url_text,{"status": tweet_text,"media_ids": media_id})

def on_error(ws,error):
    print(error)
    exit(0)

def on_close(ws):
    print("close")
    exit(0)

def connect():
    ws = websocket.WebSocketApp("ws://ionazn.org/status",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
    ws.run_forever()

if __name__ == "__main__":
    connect()
    exit(1)
