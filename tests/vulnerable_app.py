from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Welcome to XSS Vulnerable App</h1><a href='/search?q=test'>Search</a>"

@app.route("/search")
def search():
    # Reflected XSS Vulnerability
    q = request.args.get("q", "")
    return render_template_string(f"<h2>Search results for: {q}</h2>")

if __name__ == "__main__":
    app.run(port=5000)
