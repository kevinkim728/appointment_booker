# gradio_frontend.py
import gradio as gr
import requests
import json

def make_appointment_call(user_name, appointment_type, preferred_times, additional_details, business_phone):
    """Make an appointment call using the FastAPI backend"""

    # Convert preferred_times string to list (split by commas)
    times_list = [time.strip() for time in preferred_times.split(',') if time.strip()] # If theres a value in there, then add it to the list

    # Prepare the payload
    payload = {
        "user_name": user_name,
        "appointment_type": appointment_type,
        "preferred_times": times_list,
        "additional_details": additional_details,
        "business_phone": '1'+ business_phone
    }

    try:
        # Make request to your FastAPI backend
        response = requests.post("http://localhost:8000/make-call", json=payload) # response is the result of the /make-call endpoint.

        if response.status_code == 200:
            result = response.json()
            return f"✅ Call initiated successfully!\n\nCall SID: {result.get('call_sid')}\nStatus: {result.get('status')}"
        else:
            return f"❌ Error: {response.status_code}\n{response.text}"

    except Exception as e:
        return f"❌ Connection error: {str(e)}\n\nMake sure your FastAPI server is running on http://localhost:8000"

# Create Gradio interface
with gr.Blocks(title="AI Appointment Booker") as app:
    gr.Markdown("# 🤖 AI Appointment Booker")
    gr.Markdown("Fill out the details below and click 'Make Call' to have the AI assistant book your appointment.")

    with gr.Row():
        with gr.Column():
            user_name = gr.Textbox(
                label="Your Name",
                placeholder="Enter your name"
            )
            appointment_type = gr.Textbox(
                label="Appointment Type",
                placeholder="e.g., haircut, doctor appointment, restaurant reservation"
            )
            preferred_times = gr.Textbox(
                label="Preferred Times",
                placeholder="Enter times separated by commas"
            )
            business_phone = gr.Textbox(
                label="Business Phone Number",
                placeholder="Phone number to call"
            )
            additional_details = gr.Textbox(
                label="Additional Details",
                placeholder="Any special requests or details (eg. Party of 2)"
            )


    make_call_btn = gr.Button("📞 Make Call", variant="primary", size="lg")

    result_output = gr.Textbox(
        label="Call Result",
        lines=5,
        interactive=False,
        placeholder="Call results will appear here..."
    )

    # Connect the button to the function
    make_call_btn.click(
        fn=make_appointment_call,
        inputs=[user_name, appointment_type, preferred_times, additional_details, business_phone],
        outputs=result_output
    )

    gr.Markdown("---")
    gr.Markdown("💡 **Tip:** Make sure your FastAPI server is running before making calls!")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8001, share=False)
