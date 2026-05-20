from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Generic home page to validate if the server is running
@app.get("/")
async def home():
    return HTMLResponse("<h1>Twilio Realtime Server</h1><p>Server is running!</p>")

# Post request for making a call
@app.post("/make-call")
async def initiate_outbound_call():
    return {"status": "not yet implemented"}

# Starts the server
def start_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
