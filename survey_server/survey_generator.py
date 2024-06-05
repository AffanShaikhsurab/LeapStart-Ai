import json
from fastapi import FastAPI, HTTPException
from langchain_core.pydantic_v1 import BaseModel, Field
import httpx
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (replace with your frontend URL in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Replace with your SurveyHero API key
API_KEY = 'your_surveyhero_api_key_here'
BASE_URL = 'https://api.surveyhero.com/v1'

# Initialize Google Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key="AIzaSyBUspiUwI4SB_gHkU2Jd_dbb6CD3EHgxug", temperature=0.0)

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

class StartupIdea(BaseModel):
    idea: str = Field(description="The startup idea")

class SurveyQuestion(BaseModel):
    question: str  = Field("The survey question for the given set of hypotheses")

class SurveyQuestions(BaseModel):
    questions: List[SurveyQuestion]



class hypotheses(BaseModel):
    hypo: str = Field(description="The hypotheses of the given startup ")

class hypothesesList(BaseModel):
    list: List[hypotheses] 

def generate_hypotheses(idea: str):
    parser = PydanticOutputParser(pydantic_object=hypothesesList)
    prompt = PromptTemplate(
        template="\n{format_instructions}\nGenerate six hypotheses for the following startup idea: {idea}\n",
        input_variables=["idea"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    prompt_and_model = prompt | llm
    output_json = prompt_and_model.invoke({"idea": idea})
    try:
        print(str(output_json))
        output = json.loads(output_json.content.strip("```json").strip("```"))
    except:
        output = json.loads(output_json.content)
    
    return output["list"]

def generate_survey_questions(hypotheses):
    questions = []
    for hypothesis in hypotheses:
        parser = PydanticOutputParser(pydantic_object=SurveyQuestions)
        prompt = PromptTemplate(
            template="\n{format_instructions}\nGenerate a multiple choice question for users to see if they are instrested in the idea based on the following hypothesis : {hypothesis}\n",
            input_variables=["hypothesis"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        prompt_and_model = prompt | llm
        output_json = prompt_and_model.invoke({"hypothesis": hypothesis})
        try:
            output = json.loads(output_json.content.strip("```json").strip("```"))
        except:
            output = json.loads(output_json.content)
        questions.append(output["questions"])

    return questions

@app.post("/create-survey")
async def create_survey(idea: str):
    print(idea)
    hypotheses = generate_hypotheses(idea)
    questions = generate_survey_questions(hypotheses)

    survey_data = {
        "title": "Survey for Startup Idea Validation",
        "description": "We would like your feedback on these hypotheses.",
        "questions": [
            {
                "type": "multiple_choice",
                "question": question,
                "answers": [
                    {"text": "Strongly agree"},
                    {"text": "Agree"},
                    {"text": "Neutral"},
                    {"text": "Disagree"},
                    {"text": "Strongly disagree"}
                ]
            } for question in questions
        ]
    }

    print("survey_data" , str(survey_data))


# Run the server using: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


