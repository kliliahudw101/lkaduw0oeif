import pytest
import sys
import os

# Adjust sys.path to find the xsstriker module
sys.path.append(os.path.join(os.path.dirname(__file__), '../xsstriker'))

from core.ai.classifier import XSSClassifier
from core.rl.agents import EscapeAgent, SanitizationAgent
from core.engines.crawler import Crawl4AICrawler

def test_classifier_initialization():
    classifier = XSSClassifier()
    assert classifier.model is not None

def test_escape_agent():
    ea = EscapeAgent()
    action = ea.act("angle_bracket")
    assert action == "><"

def test_sanitization_agent():
    sa = SanitizationAgent()
    payload = "alert(1)"
    obfuscated = sa.obfuscate(payload, "html_entities")
    assert "&#97;" in obfuscated

def test_crawler_initialization():
    crawler = Crawl4AICrawler("http://localhost:5000")
    assert crawler.base_url == "http://localhost:5000"
