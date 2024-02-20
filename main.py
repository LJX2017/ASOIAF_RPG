from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from base_game import Game
from uuid import UUID, uuid4

app = FastAPI()

# Setup CORS for development ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# A dictionary to store game instances by session ID
games = {}


class UserInput(BaseModel):
    userInput: str
    sessionId: UUID  # Expect a session ID with each request


@app.get("/api/initial_text")
async def get_initial_text(session_id: UUID):
    """
    Endpoint to fetch initial text for a given session.
    """
    # if session_id not in games:
    games[session_id] = Game(True)
    initial_text = games[session_id].initial_loop()  # Placeholder method, implement accordingly
    print(session_id, games[session_id].chosen_event_plot)
    return {"text": initial_text}


@app.post("/api/submit_input")
async def submit_input(user_input: UserInput):
    """
    Receives user input and session ID as JSON, processes it, and returns a response.
    """
    session_id = user_input.sessionId
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Session not found")
    response_text = games[session_id].next_loop(user_input.userInput)  # Placeholder method, implement accordingly
    print(session_id, games[session_id].chosen_event_plot)
    return {"finalText": response_text}