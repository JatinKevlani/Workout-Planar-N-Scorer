import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from google import genai
from google.genai import types

from prompt import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = FastAPI()


class User(BaseModel):
    age: int
    gender: str
    heightCm: int
    weightKg: int
    bodyFatPercentage: float
    targetWeightKg: int
    targetBodyFatPercentage: float


class Preferences(BaseModel):
    goal: str
    experienceLevel: str
    daysPerWeek: int
    minutesPerWorkout: int
    planDurationWeeks: int
    includeCardio: bool
    availableEquipment: list[str]
    preferredWorkoutDays: list[str]


class Health(BaseModel):
    injuries: list[str]
    medicalConditions: list[str]
    limitations: list[str]


class WorkoutRequest(BaseModel):
    user: User
    preferences: Preferences
    health: Health


@app.get("/")
def home():
    return {
        "status": "Workout Generator API Running"
    }


@app.post("/generate-plan")
async def generate_plan(request: WorkoutRequest):

    payload = request.model_dump()

    user_prompt = f"""
Design a workout structure.

User Profile:

{json.dumps(payload, indent=2)}

Return JSON only.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )

        print("\n========== AI RESPONSE ==========\n")
        print(response.text)
        print("\n===============================\n")

        return json.loads(response.text)

    except Exception as e:

        print(e)

        return {
            "success": False,
            "error": str(e)
        }
