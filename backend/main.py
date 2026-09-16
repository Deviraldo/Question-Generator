import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


# ==================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from .env")


# ==================================================
# 2. CREATE FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="AI Question Generator",
    description="AI Question Generator using FastAPI, LangChain and Gemini",
    version="1.0.0"
)


# ==================================================
# 3. CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# 4. CREATE GEMINI MODEL
# ==================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
)


# ==================================================
# 5. CREATE QUESTION GENERATION PROMPT
# ==================================================

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert educational question generator.

Your job is to generate high-quality questions
based on the user's requirements.

Rules:

- Generate exactly the requested number of questions.
- Follow the requested difficulty level.
- Cover the requested topic.
- Follow the requested question type.
- Make questions clear and educational.
- Do not repeat questions.
- Do not provide answers unless requested.
- Number each question clearly.
"""
        ),

        (
            "human",
            """
Generate questions using the following information.

Topic:
{topic}

Number of Questions:
{number_of_questions}

Difficulty:
{difficulty}

Question Type:
{question_type}

Additional Instructions:
{additional_instructions}

Generate exactly the requested number of questions.
"""
        ),
    ]
)


# ==================================================
# 6. CREATE LANGCHAIN CHAIN
# ==================================================

question_chain = prompt | llm


# ==================================================
# 7. REQUEST MODEL
# ==================================================

class QuestionRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=2,
        max_length=500
    )

    number_of_questions: int = Field(
        ...,
        ge=1,
        le=20
    )

    difficulty: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    question_type: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    additional_instructions: str = Field(
        default="",
        max_length=2000
    )


# ==================================================
# 8. RESPONSE MODEL
# ==================================================

class QuestionResponse(BaseModel):

    questions: str


# ==================================================
# 9. ROOT ENDPOINT
# ==================================================

@app.get("/")
async def root():

    return {
        "message": "AI Question Generator API is running"
    }


# ==================================================
# 10. HEALTH CHECK
# ==================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# ==================================================
# 11. QUESTION GENERATION ENDPOINT
# ==================================================

@app.post(
    "/generate-questions",
    response_model=QuestionResponse
)
async def generate_questions(request: QuestionRequest):

    try:

        # Send user information to LangChain
        response = await question_chain.ainvoke(
            {
                "topic": request.topic,
                "number_of_questions":
                    request.number_of_questions,
                "difficulty":
                    request.difficulty,
                "question_type":
                    request.question_type,
                "additional_instructions":
                    request.additional_instructions
            }
        )

        # Get Gemini's response
        questions = response.content

        # Make sure response is a string
        if isinstance(questions, list):

            questions = " ".join(
                str(item)
                for item in questions
            )

        return QuestionResponse(
            questions=str(questions)
        )

    except Exception as e:

        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to generate questions."
        )