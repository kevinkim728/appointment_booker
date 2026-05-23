import threading
import time
from fastapi_server import start_server as start_fastapi
from gradio_frontend import app as gradio_app

def run_fastapi():
    """Run FastAPI server in a separate thread"""
    start_fastapi()

def run_gradio():
    """Run Gradio app in a separate thread"""
    gradio_app.launch(server_name="0.0.0.0", server_port=8001, share=False)

if __name__ == "__main__":
    print("🚀 Starting AI Appointment Booker...")

    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Give FastAPI time to start
    time.sleep(2)

    # Start Gradio (this will block)
    print("🌐 FastAPI running on http://localhost:8000")
    print("🎨 Starting Gradio on http://localhost:8001")
    run_gradio()
