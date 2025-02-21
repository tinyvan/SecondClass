import second_class_backend as sc
import llm
import json
import os
from colorama import init,Fore
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll,Grid
from textual.widgets import Button, Footer, Header,Label,Input,Log,Select
from textual.events import Print

init(autoreset=True) #初始化颜色ama
configFile=None#open("config.json","r",encoding='utf-8')
configJson={}
key_session=''
LLM_api_key=''
LLM_selected_service="ChatAnywhere" #Default
LLM_selected_model="" #Default
page_cache=-1

configFile=open("config.json","r+",encoding='utf-8')
try:
    configJson=json.load(configFile)
    key_session=configJson["key_session"]
    LLM_api_key=configJson["LLM_api_key"]
    page_cache=configJson["page_cache"]
    LLM_selected_service=configJson["LLM_selected_service"]
    LLM_selected_model=configJson["LLM_selected_model"]
except Exception as e:
    print(e)
    print(Fore.RED+"Error in reading config.json.Trying to init...")
    configJson={}
    key_session=''
    LLM_api_key=''
    page_cache=1

class LLMSERVICEPROVIDERSETTING(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("LLM Service Provider:",id="LLM_SERVICE_PROVIDER_LABEL")
        self.llm_service_provider_select=Select(
           [(service,service) for service in llm.get_LLM_services()],id="LLM_SERVICE_PROVIDER_SELECT")
        yield self.llm_service_provider_select
        yield Button("Load",id="LLM_LOAD")
        self.llm_model_select=Select(
            [("None","None")],id="LLM_MODEL_SELECT"
        )
        yield self.llm_model_select
    def on_select_changed(self,event:Select.Changed) -> None:
        if event.select.id=="LLM_MODEL_SELECT":
            global LLM_selected_model
            LLM_selected_model=event.select.value


    def on_mount(self) -> None:
        self.llm_service_provider_select.value=LLM_selected_service
#class LLMMODELSETTING(HorizontalGroup):
class LLMAPI(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("LLM API:",id="LLM_API_LABEL")
        self.llm_api_input=Input(value=LLM_api_key,placeholder="llm api",id="LLM_API_INPUT")
        yield self.llm_api_input
    def on_button_pressed(self) -> None:
        print("Button pressed!")
class SecretBox(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("key_session:",id="KEY_SESSION_LABEL")
        self.key_session_input=Input(value=key_session,placeholder="key_session",id="KEY_SESSION_INPUT")
        yield self.key_session_input
class InfoTable(Grid):
    def compose(self) -> ComposeResult:
        self.label_widget = Label(f"目前已到达页数:{page_cache}",id="page")
        yield self.label_widget
        self.submit_widget=Button("提交",id="submit")
        yield self.submit_widget

class MainApp(App):
    CSS_PATH = "css.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(LLMAPI(),LLMSERVICEPROVIDERSETTING(),SecretBox(),InfoTable())
    def on_button_pressed(self,event:Button.Pressed) -> None:
            if event.button.id=="LLM_LOAD":
                global LLM_api_key
                global LLM_selected_service
                llm_api_input=self.query_one(LLMAPI).llm_api_input
                if llm_api_input.value=="":
                    llm_api_input.placeholder="LLM API CANNOT BE EMPTY!"
                    return
                LLM_selected_service=self.query_one(LLMSERVICEPROVIDERSETTING).llm_service_provider_select.value

                LLM_api_key=llm_api_input.value
                llm.LLM_init(LLM_api_key,LLM_selected_service)
                LLM_model_select=self.query_one(LLMSERVICEPROVIDERSETTING).llm_model_select
                LLM_model_select.set_options([(model,model) for model in llm.get_LLM_models()])

            elif event.button.id=="submit":
                llm_api_input=self.query_one(LLMAPI).llm_api_input
                if llm_api_input.value=="":
                    llm_api_input.placeholder="LLM API CANNOT BE EMPTY!"
                    return
                key_session_input=self.query_one(SecretBox).key_session_input
                if key_session_input.value=="":
                    key_session_input.placeholder="KEY_SESSION CANNOT BE EMPTY!"
                    return
                
                
                global key_session
                
                key_session=key_session_input.value
                configJson["key_session"]=key_session
                configJson["LLM_api_key"]=LLM_api_key
                configJson["LLM_selected_service"]=LLM_selected_service
                configJson["LLM_selected_model"]=LLM_selected_model
                configJson["page_cache"]=page_cache
                configFile.seek(0)
                configFile.truncate()
                json.dump(configJson,configFile)
                self.exit(100)
                print(Fore.GREEN+"Config updated.")
            

app=MainApp()
ret=app.run()
if ret!=100:
    
    if ret==None:
        print(Fore.RED+"Exiting...")
        exit(0)
    print(Fore.RED+"Error in getting config.")
    exit(1)
sc.set_key_session(key_session)

sc.set_ssl_verify_enabled(False)
finished=0
while True:
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
            answer_text=llm.get_ans(output_to_LLM,LLM_selected_model)
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
                answer_post.append(options[ord(ans)-65]["id"])
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
            if finished>=2:
                print(Fore.GREEN+"Finished 2 questions!")
                print(Fore.GREEN+"Exiting...")
                configFile.close()
                exit(0)
    page_cache+=1
    configJson["page_cache"]=page_cache
    configFile.seek(0)
    json.dump(configJson,configFile)
    configFile.truncate()
