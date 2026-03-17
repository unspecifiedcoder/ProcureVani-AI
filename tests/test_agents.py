import pytest
from apps.agents.nodes.intent import detect_language

def test_detect_language_english():
    assert detect_language("Hello, I want to register") == "en"

def test_detect_language_hindi():
    assert detect_language("मुझे रजिस्टर करना है") == "hi"

def test_detect_language_telugu():
    assert detect_language("నేను రిజిస్టర్ చేయాలి") == "te"

def test_detect_language_empty():
    assert detect_language("") == "en"
