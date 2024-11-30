import second_class_backend as sc
import qwen
import json

sc.set_key_session("")
sc.set_secret("")
sc.set_ssl_verify_enabled(False)
qwen.Qwen_init("")

end=False
try:
    with open("page_cache","r",encoding='utf-8') as f:
        page_number=int(f.read())
except:
    page_number=1
finished=0
while not end:
    articles=sc.get_articles(str(page_number))
    
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
            answer_text=qwen.get_ans(output_to_LLM)
            print('LLM Answer:',answer_text)
            answer_post=[]
            for i in range(0,len(options)):
                if answer_text.find(chr(i+65))!=-1 or answer_text.find(chr(i+97))!=-1:
                    answer_post.append(options[i]["id"])
            
            
            if not sc.answer_questions(question_id,answer_post):
                manual_input=input("Error in answering questions.Try manual input.")
                answer_post=[]
                for i in range(0,len(options)):
                    if manual_input.find(chr(i+65))!=-1 or manual_input.find(chr(i+97))!=-1:
                        answer_post.append(options[i-1]["id"])
                if not sc.answer_questions(question_id,answer_post):
                    print("Error in manual input.")
                    exit(1)
                
            
            finished+=1
            if(finished==2):
                exit(0)
    page_number+=1
    with open("page_cache","w",encoding='utf-8') as f:
        f.write(str(page_number))
        print(f'Page {page_number} cached in file:page_cache.')
