import websocket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import xmltodict
import urllib.request
import twitter

checkusers = ['ugwis','wanimaru','dyuma','iyselee','bgpat','toga2048','tomosan26']

histogram_filename = "hist-aoj.png"

def make_histogram(filename,pid,rid,lang,cpu,mem,code):
    plt.clf()
    f = urllib.request.urlopen('http://judge.u-aizu.ac.jp/onlinejudge/webservice/solved_record?problem_id=' + str(pid) + '&language=' + lang)
    result = xmltodict.parse(f.read())
    cputime = [cpu]
    memory = [mem]
    codesize = [code]
    for solved in result['solved_record_list']['solved']:
        if solved['run_id'] != rid:
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

    print(cputime)
    print(codesize)
    print(memory)
    subplt(511,cputime,30,cpu*100,"CPU Time (ms)")

    subplt(513,codesize,30,code,"Code Size (Byte)")

    subplt(515,memory,30,mem,"Memory (KByte)")

    plt.savefig(filename)

def on_message(ws,message):
    obj = json.loads(message)
    if obj['userID'] in checkusers and obj['status'] == 4:
        problem = str(obj['problemID'])
        print(message)
        if obj['lessonID'] != "":
            problem = obj['lessonID'] + "_" + problem
        tweet_text = '[AOJ] ' + obj['userID'] + ' solved \'' + obj['problemTitle'] + '\' http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=' + problem
        make_histogram(histogram_filename,problem,obj['runID'],obj['lang'],obj['cputime'],obj['memory'],obj['code'])
        media_id = twitter.upload_image(histogram_filename)
        status = twitter.tweet({"status": tweet_text,"media_ids": media_id})

def on_error(ws,error):
    print(error)
    exit(0)

def on_close(ws):
    print("close")
    connect()
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
