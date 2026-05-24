import pytest
from twilio_openai_handler import TwilioRealtimeServer


@pytest.fixture
def server():
    return TwilioRealtimeServer()


def make_context(**kwargs):
    defaults = {
        "user_name": "Kevin",
        "appointment_type": "restaurant reservation",
        "preferred_times": ["2pm"],
        "date": "May 25, 2026",
        "additional_details": "Party of 2",
        "acceptable_range": "1pm - 4pm",
        "business_phone": "1234567890"
    }
    defaults.update(kwargs)
    return defaults


class TestGeneratePrompt:
    def test_fallback_when_no_context(self, server):
        server.call_context = None
        prompt = server.generate_prompt()
        assert "AI assistant" in prompt

    def test_user_name_in_prompt(self, server):
        server.call_context = make_context(user_name="Alice")
        prompt = server.generate_prompt()
        assert "Alice" in prompt

    def test_appointment_type_in_prompt(self, server):
        server.call_context = make_context(appointment_type="haircut")
        prompt = server.generate_prompt()
        assert "haircut" in prompt

    def test_date_in_prompt(self, server):
        server.call_context = make_context(date="June 1, 2026")
        prompt = server.generate_prompt()
        assert "June 1, 2026" in prompt

    def test_preferred_times_joined(self, server):
        server.call_context = make_context(preferred_times=["2pm", "4pm"])
        prompt = server.generate_prompt()
        assert "2pm, 4pm" in prompt

    def test_acceptable_range_in_prompt(self, server):
        server.call_context = make_context(acceptable_range="3pm - 6pm")
        prompt = server.generate_prompt()
        assert "3pm - 6pm" in prompt

    def test_additional_details_in_prompt(self, server):
        server.call_context = make_context(additional_details="Party of 4")
        prompt = server.generate_prompt()
        assert "Party of 4" in prompt

    def test_empty_preferred_times(self, server):
        server.call_context = make_context(preferred_times=[])
        prompt = server.generate_prompt()
        assert prompt  # doesn't crash, returns something

    def test_empty_acceptable_range(self, server):
        server.call_context = make_context(acceptable_range="")
        prompt = server.generate_prompt()
        assert prompt  # doesn't crash
