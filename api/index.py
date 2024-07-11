import logging
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(
    app
)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///statify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    high_score = db.Column(db.Integer, default=0)

# Initialize the database
with app.app_context():
    db.create_all()


@app.route("/api/artists", methods=["POST"])
def get_artist_info():
    try:
        content = request.json
        urls = content.get("urls")
        if not urls:
            return jsonify({"error": "No URLs provided"}), 400

        results = []

        for url in urls:
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    results.append(
                        {
                            "url": url,
                            "artist_name": "Unknown",
                            "monthly_listeners": "Unknown",
                        }
                    )
                    continue

                soup = BeautifulSoup(response.content, "html.parser")

                # Extract artist name from og:title or title
                og_title_tag = soup.find("meta", property="og:title")
                artist_name = (
                    og_title_tag["content"]
                    if og_title_tag
                    else soup.title.string.split("|")[0].strip()
                )

                # Extract monthly listeners from meta description
                meta_description_tag = soup.find("meta", {"name": "description"})
                monthly_listeners = "Unknown"
                if meta_description_tag:
                    description = meta_description_tag["content"]
                    if "monthly listeners" in description:
                        monthly_listeners = (
                            description.split("·")[-1]
                            .strip()
                            .replace("monthly listeners", "")
                            .strip()
                        )

                results.append(
                    {
                        "url": url,
                        "artist_name": artist_name,
                        "monthly_listeners": monthly_listeners,
                    }
                )
            except Exception as e:
                results.append({"url": url, "error": str(e)})

        return jsonify(results), 200
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Endpoint to create a user
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        return jsonify(id=user.id, username=user.username, high_score=user.high_score)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint to update the user's high score
@app.route('/api/users/<username>/score', methods=['PUT'])
def update_score(username):
    try:
        data = request.get_json()
        score = data.get('score')
        user = User.query.filter_by(username=username).first()
        if user:
            if score > user.high_score:
                user.high_score = score
                db.session.commit()
            return jsonify(id=user.id, username=user.username, high_score=user.high_score)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint to get the leaderboard
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        users = User.query.order_by(User.high_score.desc()).limit(10).all()
        leaderboard = [{"username": user.username, "high_score": user.high_score} for user in users]
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
