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
        """Initiate an outbound call to a business"""
        try:
            self.call_context = user_context       # user_context: dict from the initiate_outbound_call that has all the CallDetails

            # Create the payload for Twilio
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
            print(f"✅ Call initiated. Call SID: {self.current_call_sid}")
            return {
                "success": True, 
                "call_sid": self.current_call_sid, 
                "status": call.status
                }

        except Exception as e:
            print(f"❌ Failed to make outbound call: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_twilio_message(self, data, twilio_ws): # data: dict from Twilio. twilio_ws: FastAPI WebSocket object 
        """Process messages from Twilio"""
        event = data.get('event')

        if event == 'start':
            # stream just opened — connect to OpenAI and register this WebSocket so we can send audio back
            print("🎤 Call started - connecting to OpenAI")
            await self.connect_to_openai() # Opens a WebSocket connection from this server to OpenAI
            self.twilio_connections[data.get('streamSid')] = twilio_ws # Stores the key streamSid and value twilio_ws(WebSocket object) into twilio_connections dict

        elif event == 'media':
            # continuous audio chunks from Twilio — forward to OpenAI
            audio_payload = data.get('media', {}).get('payload', '')  # safely navigate nested dict, default to empty string
            if audio_payload and self.openai_ws:
                await self.send_audio_to_openai(audio_payload)

        elif event == 'stop':
            # call ended — close OpenAI connection and clean up
            print("🛑 Call ended")
            if self.openai_ws:
                await self.openai_ws.close()
                self.openai_ws = None
            stream_sid = data.get('streamSid')
            if stream_sid in self.twilio_connections:
                del self.twilio_connections[stream_sid]
