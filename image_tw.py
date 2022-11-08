import json
import urllib.request
import os, sys
from requests_oauthlib import OAuth1Session
from env import *

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"
TL = "https://api.twitter.com/1.1/statuses/user_timeline.json"

# OAuth認証 セッションを開始
twitter = OAuth1Session(CK, CS, AT, AS) #アクセスキー

userName = input("userName:") #取得したいアカウント名
GET_COUNT = int(input("Get count:"))
GET_AT_ONCE = int(input("Get at once:"))

params = {
    "screen_name":userName,       
    "count":GET_AT_ONCE,                #ツイート数（上限200)
    "include_entities":True,    #エンティティ
    "exclude_replies":False,    #返信ツイート
    "include_rts":False         #リツイート
}   

def getTL():
    global req,timeline,content
    req = twitter.get(TL,params=params)
    timeline = json.loads(req.text)

def saveContents():
    for content in timeline:        #timelineはGET_AT_ONCE個のツイートが含まれているので，contentで1つずつ選ぶ
        if "extended_entities" in content:  #画像や動画が入っている場合
            if "video_info" in content:     #動画
                print("video\n")
            else:                    # 画像
                for count, photo in enumerate(content["extended_entities"]["media"]):   
                    title = foldername+"/"+content["id_str"]+"_"+str(count)+".jpg"  #画像のタイトル
                    image_url = photo["media_url"]      #画像のurl
                    if os.path.exists(title):
                        print(f"{title} is existed")
                        continue
                    try:                             
                        urllib.request.urlretrieve(image_url,title) 
                        print(f"{title} is saved")
                    except:
                        print("error")
        else:
            print("No image")
        global num
        num = content["id"]         #最後のツイートのid

foldername = "./images/"+userName        #保存フォルダの名前
if not os.path.exists(foldername):      #ない場合
    os.makedirs(foldername)
for i in range(1,GET_COUNT):            #GET_COUNTの分だけgetTL()を呼び出す
    if(i==1):
        params = params
    else:
        params.update({"max_id":num})   #呼び出すツイートの最大id
    getTL()                         #TLをGET_AT_ONCE件取得
    saveContents()                  #画像の保存
        