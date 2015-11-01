import websocket
import time
import json
import twitterkeys

from requests_oauthlib import OAuth1Session

checklist = ['ugwis','wanimaru','dyuma','magarimame','itowo','bgpat']

URL = "https://api.twitter.com/1.1/statuses/update.json"

def tweet(text):
    params = {"status": text}
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, twitterkeys.AT, twitterkeys.AS)
    req = twitter.post(URL, params = params)
    return req.status_code

def on_message(ws,message):
    print(message)
    obj = json.loads(message)
    if obj['userID'] in checklist and obj['status'] == 4:
        status = tweet('[AOJ] ' + obj['userID'] + ' solved \'' + obj['problemTitle'] + '\' http://judge.u-aizu.ac.jp/onlinejudge/review.jsp?rid=' + str(obj['runID']))

def on_error(ws,error):
    print(error)

def on_close(ws):
    print("close")

if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://ionazn.org/status",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
    ws.run_forever()
