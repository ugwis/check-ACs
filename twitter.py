import twitterkeys
import json
from requests_oauthlib import OAuth1Session

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

def upload_image(filename):

    # OAuth認証 セッションを開始
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, 
twitterkeys.AT, twitterkeys.AS)

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

def tweet(params):
    twitter = OAuth1Session(twitterkeys.CK, twitterkeys.CS, 
twitterkeys.AT, twitterkeys.AS)
    req = twitter.post(url_text, params = params)
    return req.status_code

