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
import numpy as np
import json
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
checkusers = ['bgpat','goryudyuma','Makinami','murashin','not_seele','toga2048','ugwis','wanimaru47','tsunetoki','sn_93','scn_13k','fono09']

histogram_filename = "hist-atcoder.png"

url_atcoder_jp = "http://atcoder.jp"
contest_atcoder = "contest.atcoder.jp"
url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

filename = "hist-atcoder.png"

def regex(r,text):
    rec = re.compile(r)
    match = rec.search(text)
    if match is None:
        print("--regex doesn't matched folowing text--")
        print(text)
        return None
    return match.group(1)

def make_histogram(user,others):
    plt.clf()
    cputime = []
    memory = []
    codesize = []
    for other in others:
        cputime.append(int(other['cputime']))
        memory.append(int(other['memory']))
        codesize.append(int(other['codesize']))
    def subplt(pos,data,bins,x,xlabel):
        plt.subplot(pos)
        plt.hist(data,bins=bins,alpha=0.5)
        plt.yticks(list(map(int,np.linspace(plt.ylim()[0],plt.ylim()[1],3))))
        plt.axvline(x=x,linewidth=1,color='r')
        plt.xlabel(xlabel,size=14)
        plt.ylabel("Frequency",size=14)


    subplt(511,cputime,30,user['cputime'],"CPU Time (ms)")

    subplt(513,codesize,30,user['codesize'],"Code Size (Byte)")

    subplt(515,memory,30,user['memory'],"Memory (KByte)")

    plt.savefig(filename)
    return filename

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

def fetch_userid(uid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    userid = None
    try:
        cur.execute("""SELECT userid FROM users WHERE uid=(%s)""",(uid,))
        for row in cur:
            userid = row['userid']
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return userid

def fetch_contestid(cid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    contestid = None
    try:
        cur.execute("""SELECT contestid FROM contests WHERE cid=(%s)""",(cid,))
        for row in cur:
            contestid = row['contestid']
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return contestid

def fetch_problem(pid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    problem = None
    try:
        cur.execute("""SELECT * FROM problems WHERE pid=(%s)""",(pid,))
        for row in cur:
            problem = row
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return problem

def fetch_ended_contest_list():
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    contest = []
    try:
        cur.execute("SELECT cid,crawled FROM contests WHERE endtime <= now() AND crawled ORDER BY endtime DESC;")
        connector.commit()
        for row in cur:
            contest.append({
                "cid":row['cid'],
                "crawled":row['crawled']
            })
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return contest

def fetch_same_condition_solveds(cid,pid,lid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    solveds = []
    try:
        cur.execute("""SELECT * FROM solved WHERE cid=(%s) AND pid=(%s) AND lid=(%s);""",(cid,pid,lid))
        for row in cur:
            solveds.append(row)
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return solveds

def fetch_unchecked_solved(cid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    solved = []
    try:
        cur.execute("""SELECT * FROM solved WHERE cid=(%s) AND checked=False ORDER BY datetime DESC;""",(cid,))
        for row in cur:
            solved.append(row)
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return solved

def fetch_registers():
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    registers = []
    try:
        cur.execute("""SELECT * FROM registrants;""")
        for row in cur:
            registers.append(row['uid'])
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()
    return registers

def update_checked(rid):
    connector = psycopg2.connect(pguser.arg)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""UPDATE solved SET checked=True WHERE rid=(%s)""",(rid,))
        connector.commit()
    except Exception as e:
        print(e.message)
    cur.close()
    connector.close()

if __name__ == "__main__":
    #crawl_contest_solved_page("abc001",378)
    #crawl_contest_solved_pages("abc001","all")
    registers = fetch_registers()
    print(registers)
    contests = fetch_ended_contest_list()
    for contest in contests:
        for user in fetch_unchecked_solved(contest['cid']):
            if user['uid'] in registers:
                others = fetch_same_condition_solveds(user['cid'],user['pid'],user['lid'])
                filename = make_histogram(user,others)
                userid = fetch_userid(user['uid'])
                contestid = fetch_contestid(user['cid'])
                problem = fetch_problem(user['pid'])
                tweet_text = '[AtCoder] ' + userid + ' solved \'' + problem['title'] + '\' http://' + contestid + "." + contest_atcoder + "/tasks/" + problem['problemid']
                media_id = upload_image(filename)
                status = tweet(url_text,{"status":tweet_text,"media_ids":media_id})
            update_checked(user['rid'])
    exit(0)
