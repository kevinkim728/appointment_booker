import os
import threading
import time
from dotenv import set_key
from pyngrok import ngrok
from fastapi_server import start_server
from gradio_frontend import app as gradio_app

def start_ngrok():
    """Start ngrok tunnel and update .env with the new URL"""
    tunnel = ngrok.connect(8000)
    websocket_url = tunnel.public_url.replace("https://", "wss://") + "/media-stream"
    set_key(".env", "WEBSOCKET_URL", websocket_url)
    os.environ["WEBSOCKET_URL"] = websocket_url
    print(f"🌐 ngrok tunnel started: {tunnel.public_url}")

def run_fastapi():
    """Run FastAPI server in a separate thread"""
    start_server()

def run_gradio():
    """Run Gradio app in a separate thread"""
    gradio_app.launch(server_name="0.0.0.0", server_port=8001, share=False, inbrowser=True)

if __name__ == "__main__":
    print("🚀 Starting AI Appointment Booker...")

    start_ngrok()

    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Give FastAPI time to start
    time.sleep(2)

    # Start Gradio (this will block)
    print("🌐 FastAPI running on http://localhost:8000")
    print("🎨 Starting Gradio on http://localhost:8001")
    run_gradio()
