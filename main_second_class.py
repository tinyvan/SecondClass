import second_class_backend as sc
import llm
import json
import os
from colorama import init,Fore

init(autoreset=True) #初始化颜色ama
configFile=None#open("config.json","r",encoding='utf-8')
configJson={}
key_session=''
LLM_api_key=''
page_cache=-1
if not os.path.exists("config.json"):
    configFile=open("config.json","w",encoding='utf-8')
    key_session=input("Input key_session:\n")
    LLM_api_key=input("Input LLM_api_key:\n")
    page_cache=input("Input page:(default 1)\n")
    if page_cache=="":
        page_cache=1
    else:
        page_cache=int(page_cache)
    
    configJson["key_session"]=key_session
    configJson["LLM_api_key"]=LLM_api_key
    configJson["page_cache"]=page_cache
    json.dump(configJson,configFile)
    configFile.close()
try:
    configFile=open("config.json","r+",encoding='utf-8')
    configJson=json.load(configFile)
    key_session=configJson["key_session"]
    LLM_api_key=configJson["LLM_api_key"]
    page_cache=configJson["page_cache"]
except Exception as e:
    print(e)
    print("Error in reading config.json")
    exit(1)


sc.set_key_session(key_session)
llm.LLM_init(LLM_api_key)
end=False
finished=0
while not end:
    articles=sc.get_articles(str(page_cache))
    if not articles:
        print(Fore.RED+"Error in getting articles.KEY_SEESION MAY NEED UPDATE!!!")
        exit(1)
    for article in articles["list"]:
        if sc.check_if_answered(article):
            continue
        id=article["id"]
        article_resp=sc.get_article_by_id(id)
        if not sc.check_if_questions_exist(article_resp):
            continue
        article_content=article_resp.json()["data"]["content"]
        output_to_LLM="材料:\n"+sc.text_trim(article_content)+"\n"

        questions=sc.get_questions(id)
        for question in questions:
            output_to_LLM+="问题:\n"
            question_id=question["id"]
            question_content=question["queContent"]
            output_to_LLM+=f"{question_content}\n"
            options=question["optionList"]
            for index,option in enumerate(options,start=0):
                option_content=option["optionContent"]
                output_to_LLM+=f"{chr(index+65)}.{option_content}\n"
            print(output_to_LLM)
            answer_text=llm.get_ans(output_to_LLM)
            answer_options=[]
            print('LLM Answer:',answer_text)
            try:
                llm_json=json.loads(answer_text)
                answer_options=llm_json["answer"]
            except Exception as e:
                print(Fore.RED+"Error in parsing LLM answer.")
                print(Fore.RED+e)
            answer_post=[]
            for ans in answer_options:
                answer_post.append(options[int(ans)-65]["id"])
            # for i in range(0,len(options)):
            #     if answer_text.find(chr(i+65))!=-1 or answer_text.find(chr(i+97))!=-1:
            #         answer_post.append(options[i]["id"])
            print(answer_post)
            
            if not sc.answer_questions(question_id,answer_post):
                
                while True:
                    manual_input=input(Fore.RED+"Error in answering questions.Try manual input.\n")
                    answer_post=[]
                    for i in range(0,len(options)):
                        if manual_input.find(chr(i+65))!=-1 or manual_input.find(chr(i+97))!=-1:
                            answer_post.append(options[i-1]["id"])
                    if not sc.answer_questions(question_id,answer_post):
                        print(Fore.RED+"Error in manual input.")
                        continue
                    else:
                        break
                
            
            finished+=1
            if(finished==2):
                print(Fore.GREEN+"Finished 2 questions!")
                print(Fore.GREEN+"Exiting...")
                configFile.close()
                exit(0)
    page_cache+=1
    configJson["page_cache"]=page_cache
    configFile.seek(0)
    json.dump(configJson,configFile)
    configFile.truncate()
