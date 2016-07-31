#!/user/bin/python
# -*- coding: utf-8 -*-
import requests
import re
import sys
import psycopg2
import psycopg2.extras
import dateutil.parser
import pguser
from bs4 import BeautifulSoup

url_atcoder_jp = "http://atcoder.jp"
contest_atcoder = "contest.atcoder.jp"

def regex(r,text):
    rec = re.compile(r)
    match = rec.search(text)
    if match is None:
        print("--regex doesn't matched folowing text--")
        print(text)
        return None
    return match.group(1)

def crawl_atcoder_jp():
    global connector
    r = requests.get(url_atcoder_jp)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    contests = soup.find_all(href=re.compile("contest.atcoder.jp"))
    for contest in contests:
        contest_url = contest.get('href')
        rex = re.compile("\w*//(.*)\.contest\.atcoder\.jp\w*")
        match = rex.search(contest_url)
        if match is not None:
            cid = match.group(1)
            print(cid)
            cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute("""INSERT INTO contests(contestid) VALUES (%s)""",(cid,))
                connector.commit()
            except Exception as e:
                connector.rollback()
                print("Already inserted or Something wrong")
                print(e.message)
            cur.close()
        print("")

def insert_problem(cid,problemid,title):
    global connector
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""INSERT INTO problems(cid,problemid,title) VALUES(%s,%s,%s)""",(cid,problemid,title))
        connector.commit()
    except Exception as e:
        connector.commit()
        print(e.message)
    cur.close()

def insert_contest(contest_name,contest_begin,contest_end,contestid):
    global connector
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""UPDATE contests SET name=(%s), begintime=timestamp%s + interval '9 hours', endtime=timestamp%s + interval '9 hours' WHERE contestid=(%s)""",(contest_name,contest_begin,contest_end,contestid,))
        connector.commit()
    except Exception as e:
        connector.rollback()
        print(e.message)
    cur.close()

def crawl_contest(contestid,cid):
    url = "http://" + contestid + "." + contest_atcoder + "/assignments"
    print("crawl:" + url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    tasks = soup.find_all("tr")
    print(tasks)
    if tasks == []:
        return
    contest_name = soup.find("span",class_="contest-name").string
    print(contest_name)
    contest_term = soup.find_all("time")
    contest_begin = contest_term[0].string
    contest_end = contest_term[1].string
    print(contest_begin)
    print(contest_end)
    insert_contest(contest_name,contest_begin,contest_end,contestid)
 
    for task in tasks:
        i=0
        for td in task.find_all("td"):
            i+=1
            if i == 2:
                problemid = regex("/tasks/(\w*)",td.a.get("href"))
                title = td.a.string
                insert_problem(cid,problemid,title)
  
def fetch_contest_list():
    global connector
    print(connector)
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    contest = []
    try:
        cur.execute("""SELECT * FROM contests;""")
        connector.commit()
        for row in cur:
            contest.append({
                "contestid":row['contestid'],
                "cid":row['cid']
            })
    except Exception as e:
        connector.rollback()
        print(e.message)
    cur.close()
    return contest

if __name__ == "__main__":
    connector = psycopg2.connect(pguser.arg)
    crawl_atcoder_jp()
    contest_list = fetch_contest_list()
    print(contest_list)
    for contest in contest_list:
        try:
            crawl_contest(contest['contestid'],contest['cid'])
        except Exception as e:
            print(e.message)
    connector.close()
    exit(0)
