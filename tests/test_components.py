import pytest
from xsstriker.core.distilroberta_xss.classifier import XSSClassifier
from xsstriker.core.rl_agent.agents import EscapeAgent, SanitizationAgent
from xsstriker.core.xsstrike_integration.crawler import Crawl4AICrawler

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
