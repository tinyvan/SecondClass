import requests
import json
import hashlib

key_session=''
hfut_hardcode="9030a5ea-a52e-4033-a9b6-e64ba04c02da"
ssl_verify_enabled=True
session=requests.Session()

def set_key_session(key:str):
    global key_session
    key_session=key

def set_ssl_verify_enabled(enabled:bool):
    global ssl_verify_enabled
    ssl_verify_enabled=enabled
def make_get_headers():
    global key_session
    secret=hashlib.md5((key_session+hfut_hardcode).encode("utf-8")).hexdigest()
    if key_session=='' or secret=='':
        raise Exception("Key session or secret is not set")
    return {
 'secret':secret,
 'key_session':key_session,
 'xweb_xhr':'1',
 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11275',
 'content-type':'application/json',
 'accept':'*/*',
 'sec-fetch-site':'cross-site',
 'sec-fetch-mode':'cors',
 'sec-fetch-dest':'empty',
 'referer':'https://servicewechat.com/wx1e3feaf804330562/104/page-frame.html',
 'accept-encoding':'gzip, deflate, br',
 'accept-language':'zh-CN,zh;q=0.9'}
def make_post_headers(content_length:str):
    if key_session=='':
        raise Exception("Key sessionis not set")
    return {
 'content-length':content_length,
 'key_session':key_session,
 'xweb_xhr':'1',
 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11275',
 'content-type':'application/json',
 'accept':'*/*',
 'sec-fetch-site':'cross-site',
 'sec-fetch-mode':'cors',
 'sec-fetch-dest':'empty',
 'referer':'https://servicewechat.com/wx1e3feaf804330562/104/page-frame.html',
 'accept-encoding':'gzip, deflate, br',
 'accept-language':'zh-CN,zh;q=0.9'
 }
def get_article_by_id(id:str):
    headers=make_get_headers()
    response=session.get(f'https://dekt.hfut.edu.cn/scReports/api/wx/netlearning/{id}',headers=headers,verify=ssl_verify_enabled)
    return response

def check_if_questions_exist(resp):
    try:
        if resp.json()["data"]["rightPersent"]==None:
            return False
        if resp.json()["data"]["videoUrl"]:
            return False
        if resp.json()["data"]["rightPersent"].find("%")!=-1:
            #print(resp.json()["data"])
            return True
        else:
            return False
    except Exception as e:
        print(e)
        raise Exception("Error in checking if questions exist\n",resp.text)

def check_if_answered(response):
    return response["correct"]=="已完成"


def get_questions(id:str):
    headers=make_get_headers()
    try:
        response=session.get(f'https://dekt.hfut.edu.cn/scReports/api/wx/netlearning/questions/{id}',headers=headers,verify=ssl_verify_enabled)
        return response.json()["data"]["questions"]
    except Exception as e:
        print(e)
        raise Exception("Error in getting questions\n",response.text)
    
def answer_questions(id:str,answers:list):
    payload=json.dumps(answers).encode("utf-8")
    headers=make_post_headers(str(len(payload)))
    try:
        response=session.post(f'https://dekt.hfut.edu.cn/scReports/api/wx/netlearning/answer/{id}',headers=headers,data=payload,verify=ssl_verify_enabled)
        print(response.text)
        if response.json()["code"]==200:
            if response.json()["data"]["desc"]=="恭喜,获得积分":
                return True
        else:
            return False
 
    except Exception as e:
        print(e)
        raise Exception("Error in answering questions\n",response.text)

def get_articles(number:str):
    payload='{}'
    headers=make_post_headers(str(len(payload)))
    try:
        response=session.post(f'https://dekt.hfut.edu.cn/scReports/api/wx/netlearning/page/{number}/10',headers=headers,data=payload,verify=ssl_verify_enabled)
        return response.json()["data"]
    except Exception as e:
        print(e)
        raise Exception("Error in getting articles\n",response.text)

def text_trim(text:str):
    import bs4
    soup=bs4.BeautifulSoup(text,"html.parser")
    return soup.text