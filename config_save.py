import json

class Config:
    def __init__(self,file_name:str="config.json"):
        self.file_name=file_name
        try:
            self.file_handle=open("config.json","r+",encoding='utf-8')
        except FileNotFoundError:
            self.file_handle=open("config.json","w+",encoding='utf-8')
            print("config.json not found,create a new one.")
        try:
            self.data=json.load(self.file_handle)
        except json.JSONDecodeError:
            self.data={
                "key_session":"",
                "LLM_api_key":"",
                "LLM_selected_service":"Deepseek",
                "LLM_selected_model":"",
                "page_cache":1
            }
            print("config.json is empty or invalid, use default config.")
    def save(self):
        self.file_handle.seek(0)
        self.file_handle.truncate()
        json.dump(self.data,self.file_handle, indent=4)
        self.file_handle.flush()
    def get(self,key:str):
        return self.data[key]
    def set(self,key:str,value):
        self.data[key]=value