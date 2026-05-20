import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

class TwilioRealtimeServer:
    def __init__(self):
        self.openai_ws = None                  # holds the live WebSocket connection to OpenAI (None when no call is active)
        self.twilio_connections = {}           # maps streamSid -> Twilio WebSocket so we know where to send audio back
        self.current_call_sid = None           # Twilio's unique ID for the active call, used later to hang up
        self.twilio_client = Client(           # Twilio REST API client, authenticated with credentials from .env
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )

    async def make_outbound_call(self, business_phone: str, user_context: dict):
        self.call_context = user_context       # a dict from the initiate_outbound_call that has all the CallDetails

        call = self.twilio_client.calls.create(
            to=business_phone,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            url=f"{os.getenv('WEBSOCKET_URL').replace('wss://', 'https://').replace('/media-stream', '')}/webhook/voice",  # Webhook for making the call
            method='POST',
            record=True,
            recording_channels='mono',
            recording_status_callback=f"{os.getenv('WEBSOCKET_URL').replace('wss://', 'https://').replace('/media-stream', '')}/recording"  # Webhook for recording the call
        )

        self.current_call_sid = call.sid       # save the call ID so we can hang up later
        return {"success": True, "call_sid": self.current_call_sid, "status": call.status}
