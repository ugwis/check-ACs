import websocket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import xmltodict
import twitter
import requests

checkusers = ['ugwis','wanimaru','dyuma','iyselee','bgpat','toga2048','tomosan26','aota']

histogram_filename = "hist-aoj.png"

def make_histogram(savefile,pid,your_rid,lang,your_cpu,your_mem,your_code):
    plt.clf()
    r = requests.get('http://judge.u-aizu.ac.jp/onlinejudge/webservice/solved_record?problem_id=' + str(pid) + '&language=' + lang)
    result = xmltodict.parse(r.text.encode(r.encoding))
    cputime = [your_cpu]
    memory = [your_mem]
    codesize = [your_code]
    for solved in result['solved_record_list']['solved']:
        if solved['run_id'] != your_rid:
            cputime.append(int(solved['cputime'])*100)
            memory.append(int(solved['memory']))
            codesize.append(int(solved['code_size']))
    
    def add_subplt(plt_pos,data,bins,your_data,xlabel):
        plt.subplot(plt_pos)
        plt.hist(data,bins=bins,alpha=0.5)
        plt.yticks(list(map(int,np.linspace(plt.ylim()[0],plt.ylim()[1],3))))
        plt.axvline(x=your_data,linewidth=1,color='r')
        plt.xlabel(xlabel,size=14)
        plt.ylabel("Frequency",size=14)

    add_subplt(511,cputime,30,your_cpu*100,"CPU Time (ms)")

    add_subplt(513,codesize,30,your_code,"Code Size (Byte)")

    add_subplt(515,memory,30,your_mem,"Memory (KByte)")

    plt.savefig(savefile)

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
