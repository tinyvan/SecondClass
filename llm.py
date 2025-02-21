from openai import OpenAI

LLM_SERVICES={
    "ChatAnywhere":"https://api.chatanywhere.tech/v1",
    "Google Gemini":"https://generativelanguage.googleapis.com/v1beta/openai/"
}

system_prompt="""
You are highly skilled in analyzing Chinese text and are proficient in answering questions based on the information provided in the text. Your responses should follow the structure of the JSON format, providing clear and concise answers based on the analysis of the text.
Usually the answer can be easily found in the text.
You should provide your thinking process in the "thinking" field of the JSON response.
Your responses should be the following format and answer letter must be in uppercase.:
{
"thinking":"Your thinking process should be put here",
"answer":["A","B","C"]
}
"""

client = None
def LLM_init(api_key:str,service:str):
    global client
    client=OpenAI(
    api_key=api_key, 
    base_url=LLM_SERVICES[service],
    )


def get_ans(text,model:str):
    if client==None:
        raise Exception("LLM is not initialized")
    completion = client.chat.completions.create(
    model=model,
    response_format={"type":"json_object"},
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': text}],
    )
    return completion.choices[0].message.content
def get_LLM_services():
    return list(LLM_SERVICES.keys())

def get_LLM_models():
    if client==None:
        raise Exception("LLM is not initialized")
    model_list=client.models.list().data
    return [model.id for model in model_list]
#FOR TEST
if __name__=="__main__":
    LLM_init("")
    print(get_ans("""
"question":"The cat have abilities like ()"
    "options":[
        "A.Able to jump",
        "B.Able to catch mouse".
        "C.Can clean the table",
        "D.love to eat fish"
    ]"""))