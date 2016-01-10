#!/user/bin/python
# -*- coding: utf-8 -*-
import requests
import re
import sys
import psycopg2
import psycopg2.extras
import dateutil.parser
import twitterkeys
import pguser
import matplotlib.pyplot as plt
import numpy as np
import json
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup

checkusers = ['bgpat','goryudyuma','Makinami','murashin','not_seele','toga2048','ugwis','wanimaru47','tsunetoki']

histogram_filename = "hist-atcoder.png"

url_atcoder_jp = "http://atcoder.jp"
contest_atcoder = "contest.atcoder.jp"
url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

def make_histogram(filename,pid,rid,lang,cpu,mem,code):
    plt.clf()
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM solved WHERE pid='" + pid + "' AND lang='" + lang + "'")
    cputime = [cpu]
    memory = [mem]
    codesize = [code]
    for row in cur:
        if row['rid'] != rid:
            cputime.append(int(row['cpu_time']))
            memory.append(int(row['memory_usage']))
            codesize.append(int(row['code_size']))
    def subplt(pos,data,bins,x,xlabel):
        plt.subplot(pos)
        plt.hist(data,bins=bins,alpha=0.5)
        plt.yticks(list(map(int,np.linspace(plt.ylim()[0],plt.ylim()[1],3))))
        plt.axvline(x=x,linewidth=1,color='r')
        plt.xlabel(xlabel,size=14)
        plt.ylabel("Frequency",size=14)

    print(cputime)
    print(codesize)
    print(memory)

    subplt(511,cputime,30,cpu,"CPU Time (ms)")

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

def regex(r,text):
    rec = re.compile(r)
    match = rec.search(text)
    if match is None:
        print("--regex doesn't matched folowing text--")
        print(text)
        return None
    return match.group(1)

def crawl_contest(url):
    print(url)
    ret = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    succ = soup.find_all("tr")
    if succ == []:
        return None
    for suc in succ:
        row = suc.find_all("td")
        if row == []:
            continue
        try:
            ret.append({
                "timestamp": dateutil.parser.parse(row[0].time.string),
                "problem": regex("/tasks/(\w*)",row[1].a.get("href")),
                "problemTitle":row[1].a.string,
                "problemURL":row[1].a.get("href"),
                "userid": regex("/users/(\w*)",row[2].a.get("href")),
                "username": row[2].a.string,
                "lang": row[3].string,
                "score": row[4].string,
                "code_size": regex("(\d*) Byte",row[5].string),
                "cpu_time": regex("(\d*) ms",row[7].string),
                "memory_usage": regex("(\d*) KB",row[8].string),
                "rid": regex("/submissions/(\d*)",row[9].a.get("href"))
            })
        except:
            print(url + ":exception")
    return ret

def insert(cid):
    i = 1
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    while True:
        data = crawl_contest("http://" + cid + "." + contest_atcoder + "/submissions/all/" + str(i) + "?status=AC")
        if data is None:
            break
        for solved in data:
            tup = (solved['rid'],solved['problem'],solved['userid'],solved['lang'],solved['score'],solved['code_size'],solved['cpu_time'],solved['memory_usage'],solved['timestamp'])
            try:
                cur.execute("""INSERT INTO solved (rid,pid,userid,lang,score,code_size,cpu_time,memory_usage,data) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",tup)
                connector.commit()
                print(solved['userid'] + " > " + solved['problem'])
            except:
                connector.commit()
                return
            if solved['userid'] in checkusers:
                tweet_text = '[AtCoder] ' + solved['userid'] + ' solved \'' + solved['problemTitle'] + '\' http://' + cid + "." + contest_atcoder + solved['problemURL']
                make_histogram(histogram_filename,solved['problem'],solved['rid'],solved['lang'],int(solved['cpu_time']),int(solved['memory_usage']),int(solved['code_size']))
                media_id = upload_image(histogram_filename) 
                status = tweet(url_text,{"status":tweet_text,"media_ids":media_id})
        i+=1

def crawl_atcoder_jp():
    cur = connector.cursor()
    r = requests.get(url_atcoder_jp)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    contests = soup.find_all(href=re.compile("contest.atcoder.jp"))
    for contest in contests:
        contest_url = contest.get('href')
        rex = re.compile("\w*//(\w*)\.contest\.atcoder\.jp\w*")
        match = rex.search(contest_url)
        if match is not None:
            print(match.group(1))
            try:
                cur.execute("INSERT INTO contest(cid) VALUES (%s)",[match.group(1)])
                connector.commit()
            except:
                print("Already inserted or Something wrong")
    cur.close()

def update_solvedlist():
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM contest;")
    contest = []
    for row in cur:
        contest.append(row['cid'])
    cur.close()
    cur = connector.cursor()
    for cid in contest:
        insert(cid)
    cur.close()

if __name__ == "__main__":
    param = sys.argv

    connector = psycopg2.connect(pguser.arg)

    if len(param) == 1:
        update_solvedlist()
    elif param[1] == "-update-contest-list":
        crawl_atcoder_jp()

   
    connector.close()
    exit(0)
