from openai import OpenAI


system_prompt="""
#You are an excellent text analyzer and you are expert at outputting json.
#You follow user's instructions strictly
#You only need to answer the capital letter before the option, no need to explain the content of the question
#You will be given gift if you strictly follow user's instructions.
#Ouput example:
#["A","B","C"]
"""
client = None
def Qwen_init(api_key:str):
    global client
    client=OpenAI(
    api_key=api_key, 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def get_ans(text):
    if client==None:
        raise Exception("Qwen is not initialized")
    completion = client.chat.completions.create(
    model="qwen-plus",
    response_format={"type":"json_object"},
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': text}],
    )
    return completion.choices[0].message.content

#FOR TEST
if __name__=="__main__":
    print(get_ans("""
"question":"The cat have abilities like ()"
    "options":[
        "A.Able to jump",
        "B.Able to catch mouse".
        "C.Can clean the table",
        "D.love to eat fish"
    ]"""))