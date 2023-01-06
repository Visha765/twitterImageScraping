import json
import urllib.request
import os, sys
from requests_oauthlib import OAuth1Session
from env import *

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"
TL = "https://api.twitter.com/1.1/statuses/user_timeline.json"

# OAuth認証 セッションを開始
twitter = OAuth1Session(*[ENV[key] for key in ("CK", "CS", "AT", "AS")]) #アクセスキー

userName = input("userName:") #取得したいアカウント名
GET_COUNT = min(int(input("Get count:")), 200)
GET_AT_ONCE = min(int(input("Get at once:")), 200)
CONTINUE = input("?continue if exist images found (y/n):") == 'y'

params = {
    "screen_name":userName,       
    "count":GET_AT_ONCE,                #ツイート数（上限200)
    "include_entities":True,    #エンティティ
    "exclude_replies":False,    #返信ツイート
    "include_rts":False         #リツイート
}   

# imageFolder = "./images/"+userName        
imageFolder = os.path.join("./images", userName)  #保存フォルダの名前
if not os.path.exists(imageFolder):      #ない場合
    os.makedirs(imageFolder)

class Log():
    def __init__(self):
        folder = "./log"
        if not os.path.exists(folder):      #ない場合
            os.makedirs(folder)
        self.logPath = os.path.join(folder, f"{userName}.txt")  #ログのパス
    
        self.log = self.get()
    
    def get(self):
        log = []
        if os.path.exists(self.logPath):
            with open(self.logPath, mode='r') as f:
                log = [s.strip() for s in f.readlines()]
        else:
            open(self.logPath, mode='a+')
        return log
    
    def write(self):
        with open(self.logPath, mode='w') as f:
            f.write('\n'.join(self.log))
    
    def exists(self, title):
        if title in self.log:
            return True
        else:
            self.log.append(title)
            return False

def getTL():
    global req,timeline,content
    req = twitter.get(TL,params=params)
    timeline = json.loads(req.text)

def saveContents():
    log = Log()
    for content in timeline:        #timelineはGET_AT_ONCE個のツイートが含まれているので，contentで1つずつ選ぶ
        if "extended_entities" in content:  #画像や動画が入っている場合
            if "video_info" in content:     #動画
                print("video\n")
            else:                    # 画像
                for count, photo in enumerate(content["extended_entities"]["media"]):   
                    title = f"{content['id_str']}_{str(count)}.jpg"  #画像のタイトル
                    imagePath = os.path.join(imageFolder, title)    #画像のパス
                    image_url = photo["media_url"]      #画像のurl
                    if log.exists(title):
                        log.exists(title)
                        print(f"{title} is existed")
                        if CONTINUE:
                            continue
                        else:
                            sys.exit()
                    try:                             
                        urllib.request.urlretrieve(image_url, imagePath) 
                        print(f"{title} is saved") 
                        
                    except:
                        print("error")
        else:
            print("No image")
        global num
        num = content["id"]         #最後のツイートのid
    log.write()

for i in range(1,GET_COUNT):            #GET_COUNTの分だけgetTL()を呼び出す
    if(i==1):
        params = params
    else:
        params.update({"max_id":num})   #呼び出すツイートの最大id
    getTL()                         #TLをGET_AT_ONCE件取得
    saveContents()                  #画像の保存
        