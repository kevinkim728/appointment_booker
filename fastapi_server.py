import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import List, Optional
from twilio.twiml.voice_response import VoiceResponse
from twilio_openai_handler import TwilioRealtimeServer

load_dotenv()
#Initializr FastAPI app and server
app = FastAPI()
server = TwilioRealtimeServer()

class CallDetails(BaseModel):
    user_name: str = "user name"
    appointment_type: str = "restaurant reservation"
    preferred_times: List[str] = ["Tuesday 12-2"]
    user_phone: str = "your-phone-number"
    additional_details: Optional[str] = "Party for 2"
    business_phone: str = "business-phone-number"

@app.get("/")
async def home():
    """
    Generic home page to validate if the server is running
    """
    return HTMLResponse("<h1>Twilio Realtime Server</h1><p>Server is running!</p>")

# This is the entry point
@app.post("/make-call")
async def initiate_outbound_call(request: CallDetails):
    """
    API endpoint to initiate outbound calls. 
    Accepts CallDetails, strips out the business phone
    Triggers the outbound call
    """
    user_context = request.model_dump()             # converts CallDetails Pydantic model to plain dict
    business_phone = user_context['business_phone']
    
    if not business_phone:
      return {"error": "business_phone is required"}

    # Gets business_phone then passes it to Twilio
    result = await server.make_outbound_call(business_phone, user_context) 
    return result

# Twilio hits this when the call connects — responds with TwiML instructing Twilio to open a WebSocket stream
@app.post("/webhook/voice")
async def handle_voice_webhook():
    """Handles incoming and outgoing Twilio voice calls"""
    response = VoiceResponse() # Creates a TwiML object with a <Response> element
    connect = response.connect() # Creates a <Connect> element in <response>
    connect.stream(url=os.getenv('WEBSOCKET_URL')) # Creates a <Stream> element in <Connect>. WEBSOCKET_URL directs them to the /media-stream webhook.
    return Response(content=str(response), media_type="application/xml") # Converts the TwiML object into a string and returns to Twilio

@app.post("/recording")
async def handle_recording_webhook(request: Request):
    form_data = await request.form() # Twilio sends recording callbacks as .form() data, not JSON. So instead of request.json() we use request.form().
    recording_url = form_data.get('RecordingUrl') # we extract the fields we need. Twilio sends a bunch of fields
    call_sid = form_data.get('CallSid') # these three are the ones we care about: the URL to download the audio, the call ID, and the recording ID.
    recording_sid = form_data.get('RecordingSid')
    recording_duration = form_data.get('RecordingDuration')

    print(f"📼 Recording completed: {recording_sid}")
    print(f"🔗 Recording URL: {recording_url}")
    print(f"⏱️  Duration: {recording_duration} seconds")
    
    await server.transcribe_recording(recording_url, call_sid, recording_sid)

    return {"status": "received"}

@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Twilio Media Streams"""
    await websocket.accept() # .accept() opens the door for Twilio and establishes the connection
    print("Twilio connected via FastAPI WebSocket")
    
    try:
        while True:
            data = await websocket.receive_text() # Waits and when Twilio sends something .receive_text() returns it as a JSON string
            message = json.loads(data) # Turns that JSON string into a python dict
            await server.handle_twilio_message(message, websocket) # calls handle_twilio_message with that python dict and the Websocket object
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Twilio WebSocket disconnected")

# Starts the server
def start_server():
    """Start the FastAPI Server"""
    print("🌐 Starting FastAPI server on port 8000")
    print("📞 WebSocket ready on same port at /media-stream")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()