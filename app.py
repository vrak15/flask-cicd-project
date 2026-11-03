from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Flask CI/CD Application</h1>
    <h2>Deployment Successful!</h2>
    <p>Deployed using Jenkins, Docker, GitHub and AWS EC2.</p>
    """

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "flask-cicd-app",
        "version": os.getenv("APP_VERSION", "local")
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
