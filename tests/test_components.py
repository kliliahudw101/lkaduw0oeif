import pytest
from xsstriker.core.distilroberta_xss.classifier import XSSClassifier
from xsstriker.core.rl_agent.agents import EscapeAgent, SanitizationAgent
from xsstriker.core.xsstrike_integration.crawler import SimpleCrawler

def test_classifier_initialization():
    classifier = XSSClassifier()
    assert classifier.model is not None

def test_escape_agent():
    ea = EscapeAgent()
    action = ea.act()
    assert action in ea.rules

def test_sanitization_agent():
    sa = SanitizationAgent()
    payload = "<script>"
    obfuscated = sa.obfuscate(payload)
    assert isinstance(obfuscated, str)

def test_crawler_initialization():
    crawler = SimpleCrawler("http://localhost:5000")
    assert crawler.base_url == "http://localhost:5000"
