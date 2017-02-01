#!/user/bin/python
# -*- coding: utf-8 -*-
import requests
import os
import re
import sys
import psycopg2
import psycopg2.extras
import dateutil.parser
import pguser
from selenium import webdriver
from bs4 import BeautifulSoup

url_atcoder_jp = "https://atcoder.jp"
contest_atcoder = "contest.atcoder.jp"

def regex(r,text):
    rec = re.compile(r)
    match = rec.search(text)
    if match is None:
        print("--regex doesn't matched folowing text--")
        print(text)
        return None
    return match.group(1)

def crawl_contest_list(page):
    global connector
    url = url_atcoder_jp + "/contest/archive?lang=ja&p=" + str(page)
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    contests = soup.find_all(href=re.compile("contest.atcoder.jp"))
    inserted_count = 0
    for contest in contests:
        contest_url = contest.get('href')
        rex = re.compile("\w*//(.*)\.contest\.atcoder\.jp\w*")
        match = rex.search(contest_url)
        if match is not None:
            cid = match.group(1)
            cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute("""INSERT INTO contests(contestid) SELECT %s WHERE NOT EXISTS (SELECT 1 FROM contests WHERE contestid=%s)""",(cid,cid))
                connector.commit()
                inserted_count += 1
            except Exception as e:
                connector.rollback()
                print("Already inserted or Something wrong")
                print(e.message)
            cur.close()
    next_page = soup.find_all(href=re.compile("p=" + str(page+1)))
    if len(next_page):
        crawl_contest_list(page+1)

def insert_problem(cid,problemid,title):
    global connector
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""INSERT INTO problems(cid,problemid,title) VALUES(%s,%s,%s)""",(cid,problemid,title))
        connector.commit()
    except Exception as e:
        connector.commit()
        #print(e.MESsage)
    cur.close()

def insert_contest(contest_name,contest_begin,contest_end,contestid):
    global connector
    cur = connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""UPDATE contests SET name=(%s), begintime=timestamp%s + interval '9 hours', endtime=timestamp%s + interval '9 hours' WHERE contestid=(%s)""",(contest_name,contest_begin,contest_end,contestid,))
        connector.commit()
    except Exception as e:
        connector.rollback()
        #print(e.message)
    cur.close()

def crawl_contest(contestid,cid):
    url = "http://" + contestid + "." + contest_atcoder + "/assignments"
    #print(url)
    r = requests.get(url)
    #print(r.text.encode(r.encoding))
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    tasks = soup.find_all("tr")
    #print(tasks)
    if tasks == []:
        return
    contest_name = soup.find("span",class_="contest-name").string.encode('utf-8')
    #print("contest name: " + contest_name)
    contest_term = soup.find_all("time")
    contest_begin = contest_term[0].string
    contest_end = contest_term[1].string
    #print("contest begin: " + contest_begin)
    #print("contest end: " + contest_end)
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
    crawl_contest_list(1)
    contest_list = fetch_contest_list()
    for contest in contest_list:
        print('crawling: ' + contest['contestid'])
        try:
            crawl_contest(contest['contestid'],contest['cid'])
        except Exception as e:
            print(e.message)
    connector.close()
    exit(0)
