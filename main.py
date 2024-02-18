from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from base_game import Game
app = FastAPI()

# Setup CORS for development ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files, assuming your frontend HTML is placed under 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Example game instance
game = None


class UserInput(BaseModel):
    userInput: str


@app.get("/api/initial_text")
async def get_initial_text():
    """
    Endpoint to fetch initial text to be displayed in the frontend input box.
    """
    # This could be fetching the initial game state or any other relevant information
    game = Game()
    initial_text = game.initial_loop()  # Placeholder method, implement accordingly
    return {"text": initial_text}


@app.post("/api/submit_input")
async def submit_input(user_input: UserInput):
    """
    Receives user input as JSON, processes it, and returns a response.
    """
    # Process the input using your game logic
    response_text = game.next_loop(user_input.userInput)  # Placeholder method, implement accordingly
    return {"finalText": response_text}

# You may remove or adapt the existing '/api/input/' and '/api/data/' endpoints as they are not directly used by the revised frontend logic.
