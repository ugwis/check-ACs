#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import twitterkeys
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1Session

URL = "https://api.twitter.com/1.1/statuses/update.json"

checklist = ['bgpat','goryudyuma','Makinami','murashin','not_seele','toga2048','ugwis','wanimaru47']

def tweet(text):
    params = {"status": text}
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, twitterkeys.AT, twitterkeys.AS)
    req = twitter.post(URL, params = params)
    return req.status_code

def save(filename,sucArr):
    fd = open(filename,'w')
    try:
        fd.write(json.dumps(sucArr))
    except:
        print('tsurai')
    finally:
        fd.close()

def check_user(user):
    print('check ' + user + '\'s ACs')
    # scraping
    url = 'http://kenkoooo.com/atcoder/index.php?name=' + user
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"html.parser")
    succ = soup.find_all(class_="success")

    # file load
    filename = './solvedlist/' + user + '.json'
    sucArr = []
    modf = False

    try:
        fd = open(filename,'r')
        sucArr = json.loads(fd.read())

    except:
        for suc in succ:
            problemURL = suc.a.get('href')
            sucArr.append(problemURL)
            modf = True

    else:#check new AC
        fd.close()
        for suc in succ:
            print(suc)
            problemURL = suc.a.get('href')
            problemName = suc.a.string
            if problemURL is None or problemName is None:
                break
            print(problemURL)
            print(problemName)
            if not problemURL in sucArr:
                sucArr.append(problemURL)
                status = tweet('[AtCoder] ' + user + ' solved \'' + problemName + '\' ' + problemURL)
                modf = True

    if modf:
        save(filename,sucArr)

if __name__ == "__main__":
    for user in checklist:
        check_user(user)
    exit(0)
