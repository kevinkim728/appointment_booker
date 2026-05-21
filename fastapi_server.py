import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import List, Optional
from twilio.twiml.voice_response import VoiceResponse
from twilio_openai_handler import TwilioRealtimeServer

app = FastAPI()
server = TwilioRealtimeServer()

class CallDetails(BaseModel):
    user_name: str = "user name"
    appointment_type: str = "restaurant reservation"
    preferred_times: List[str] = ["Tuesday 12-2"]
    user_phone: str = "your-phone-number"
    additional_details: Optional[str] = "Party for 2"
    business_phone: str = "business-phone-number"

# Generic home page to validate if the server is running
@app.get("/")
async def home():
    return HTMLResponse("<h1>Twilio Realtime Server</h1><p>Server is running!</p>")

# Accepts appointment details, strips out the business phone, and triggers the outbound call
@app.post("/make-call")
async def initiate_outbound_call(request: CallDetails):
    user_context = request.model_dump()                       # convert Pydantic model to plain dict
    business_phone = user_context['business_phone'] # separate business_phone — passed to Twilio, not to the prompt
    result = await server.make_outbound_call(business_phone, user_context)
    return result

# Twilio hits this when the call connects — responds with TwiML instructing Twilio to open a WebSocket stream
@app.post("/webhook/voice")
async def handle_voice_webhook(request: Request):
    response = VoiceResponse()
    connect = response.connect()
    connect.stream(url=os.getenv('WEBSOCKET_URL'))
    return Response(content=str(response), media_type="application/xml")

# Starts the server
def start_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
