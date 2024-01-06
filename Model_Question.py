from http import client
import json
import re
import PyPDF2
from click import File
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import logging
import json5
from openai import OpenAI
from apikey import myapikey


app = FastAPI()

client = OpenAI(
    api_key=myapikey(),
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

output = "Default Text"


def extract_text_from_pdf(file):
    i = 1
    ToKeep = False
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page_num in range(len(pdf_reader.pages)):
        pdf_text = pdf_reader.pages[page_num].extract_text(Tj_sep=" ", TJ_sep=" ")
        txt_parts = pdf_text.split("\n")
        txt = "  ".join(txt_parts).lower()
        if f"chapter{i}" in txt:
            text += f"\n\n Chapter {i} \n " + txt + "\n"
            i += 1
            ToKeep = True
        elif f"chapter {i}" in txt:
            text += f"\n\n Chapter {i} \n " + txt + "\n"
            i += 1
            ToKeep = True
        # if ToKeep:
        #     if f"chapter{i}" in txt:
        #         i += 1
        #         text += "\n\n" + txt + "\n"
        #     else:
        #         text += " " + txt + "\n"
        if len(text) > 3500:
            break
    if len(text) == 0:
        for page_num in range(len(pdf_reader.pages)):
            pdf_text = pdf_reader.pages[page_num].extract_text(Tj_sep=" ", TJ_sep=" ")
            txt_parts = pdf_text.split("\n")
            txt = "  ".join(txt_parts).lower()
            text += f"\n\n Chapter {i} \n " + txt + "\n"
            i += 1
            if len(text) > 3500:
                break
    return text


def chat_gpt(prompt, num_questions, difficulty, types):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"""Ask {num_questions} questions of objective questions of type
                {types}  only no other type.based on 
                the text i am providing you must mention its answer, its difficulty level,the 
                chapter from where it was taken and mention question number 
                for every question these are must
                the question difficulty level should be around
                {difficulty}.Ensure that questions 
                cover all chapters within the book text I Provided, 
                it is must that there should be diffrent type questions but within {type} only
                and they should cover question from every 
                chapter not from only one chapter, 
                The Output YOU Provide MUST BE IN WELL FORMATED JSON
                The book text data is given below:\n\n{prompt}""",
            }
        ],
    )
    generated_text = response.choices[0].message.content
    return generated_text


@app.post("/")
async def generate_quiz(
    pdf_file: UploadFile = File(...),
    num_questions: int = 20,
    difficulty: str = "medium",
    types: str = "MCQ , True/False and Fill in The Blanks",
):
    try:
        global output
        pdf_text = extract_text_from_pdf(pdf_file.file)
        questions = chat_gpt(pdf_text, num_questions, difficulty, types)
        print(questions)
        questions = questions.replace("\\n", "")
        questions = questions.replace("\n", "")
        data = json.loads(questions)
        output = data
        return output

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/")
async def api_info():
    return output


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=80)
