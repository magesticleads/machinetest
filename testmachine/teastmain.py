from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import openai

# openai api key
openai.api_key = os.getenv("OPENAI_API_KEY")

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI API


# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Define the Character model
class Character(BaseModel):
    name: str
    details: str

# to  add a character
@app.post("/add_character")
async def add_character(character: Character):
    print(character)
    data = {
        "name": character.name,
        "details": character.details
    }
    response = supabase.table("characters").insert(data).execute()
    print(response)
    if response.status_code != 201:
        raise HTTPException(status_code=400, detail="Character could not be added")
    return {"message": "Character added successfully"}

# to generate a story
@app.post("/generate_story/{character_name}")
async def generate_story(character_name: str):
    response = supabase.table("characters").select("*").eq("name", character_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Character not found  please try again")
    character_data = response.data[0]
    prompt = f"Write a short story about {character_data['name']}, {character_data['details']}."
    openai_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    print(openai_response)
    print("*"*100)
    print(openai_response.choices[0].message.content)
    
    story = openai_response.choices[0].message.content
    return {"story": story}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
