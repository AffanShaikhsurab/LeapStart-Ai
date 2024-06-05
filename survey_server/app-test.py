import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key="AIzaSyBUspiUwI4SB_gHkU2Jd_dbb6CD3EHgxug", temperature=0.0)
SCOPES = ["https://www.googleapis.com/auth/forms.body"  , "https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/forms.responses.readonly" ]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

class StartupIdea(BaseModel):
    idea: str = Field(description="The startup idea")

class SurveyQuestion(BaseModel):
    question: str = Field(description="The survey question for the given set of hypotheses")

class SurveyQuestions(BaseModel):
    questions: List[SurveyQuestion]

class Hypothesis(BaseModel):
    hypo: str = Field(description="The hypothesis of the given startup")

class HypothesisList(BaseModel):
    list: List[Hypothesis]

def generate_hypotheses(idea: str):
    parser = PydanticOutputParser(pydantic_object=HypothesisList)
    prompt = PromptTemplate(
        template="\n{format_instructions}\nGenerate six hypotheses for the following startup idea: {idea}\n",
        input_variables=["idea"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    prompt_and_model = prompt | llm
    output_json = prompt_and_model.invoke({"idea": idea})
    try:
        print(output_json.content)
        output = json.loads(output_json.content.strip("```json").strip("```"))
    except:
        output = json.loads(output_json.content)
    
    return output["list"]

def generate_survey_questions(hypotheses):
    questions = []
    for hypothesis in hypotheses:
        parser = PydanticOutputParser(pydantic_object=SurveyQuestions)
        prompt = PromptTemplate(
            template="\n{format_instructions}\nGenerate a multiple choice question for users to see if they are interested in the idea based on the following hypothesis: {hypothesis}\n",
            input_variables=["hypothesis"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        prompt_and_model = prompt | llm
        output_json = prompt_and_model.invoke({"hypothesis": hypothesis})
        try:
            output = json.loads(output_json.content.strip("```json").strip("```"))
        except:
            output = json.loads(output_json.content)
        questions.append(output["questions"][0]["question"])

    return questions

def create_google_form(survey_data):
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("./client_secrets.json", SCOPES)
        creds = tools.run_flow(flow, store)
    
    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )

    # Create form with only the title
    form_body = {
        "info": {
            "title": survey_data["title"],
        }
    }

    form_result = form_service.forms().create(body=form_body).execute()
    form_id = form_result["formId"]

    # Add description and questions
    form_requests = [
        {
            "updateFormInfo": {
                "info": {
                    "description": survey_data["description"],
                },
                "updateMask": "description"
            }
        }
    ]

    for question in survey_data["questions"]:
        form_requests.append({
            "createItem": {
                "item": {
                    "title": question["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": answer["text"]} for answer in question["answers"]],
                                "shuffle": True,
                            },
                        }
                    },
                },
                "location": {"index": 0},
            }
        })

    batch_update_body = {"requests": form_requests}
    form_service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()

    form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    return form_id, form_url

def combine_responses_with_questions(form_questions, form_responses):
    # Create a mapping from questionId to question title
    question_id_to_title = {}
    for item in form_questions["items"]:
        question_id = item["questionItem"]["question"]["questionId"]
        question_title = item["title"]
        question_id_to_title[question_id] = question_title

    # Combine responses with questions
    combined_responses = []
    for response in form_responses["responses"]:
        combined_response = {"responseId": response["responseId"], "createTime": response["createTime"], "answers": []}
        for question_id, answer in response["answers"].items():
            question_title = question_id_to_title.get(question_id, "Unknown Question")
            combined_response["answers"].append({
                "question": question_title,
                "response": answer["textAnswers"]["answers"][0]["value"]
            })
        combined_responses.append(combined_response)

    return combined_responses
def get_google_form(form_id):
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
        creds = tools.run_flow(flow, store)
    
    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )

    form_result = form_service.forms().get(formId=form_id).execute()
    return form_result

@app.post("/create-survey")
async def create_survey(idea: str):
    hypotheses = generate_hypotheses(idea)
    questions = generate_survey_questions(hypotheses)

    survey_data = {
        "title": "Survey for Startup Idea Validation",
        "description": "We would like your feedback on these hypotheses.",
        "questions": [
            {
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

    form_id, survey_url = create_google_form(survey_data)
    return {"form_id": form_id, "url": survey_url}

def get_google_form_responses(form_id):
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )

    responses = form_service.forms().responses().list(formId=form_id).execute()
    return responses


@app.get("/get-form-response")
async def get_form(form_id: str):
    try:
        form_question = get_google_form(form_id=form_id)
        form_data = get_google_form_responses(form_id)
        output = combine_responses_with_questions( form_question , form_responses=form_data)
        return output 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-form")
async def get_form(form_id: str):
    try:
        form_data = get_google_form(form_id)
        return form_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
