from flask import Flask, render_template, request, jsonify
from skill_gap_engine import analyze_role_gap
from db_queries import get_all_roles

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/assessment")
def assessment():
    return render_template("assessment.html")

if __name__ == "__main__":
    app.run(debug=True)
