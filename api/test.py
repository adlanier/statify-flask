from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/test", methods=["GET", "OPTIONS"])
def test():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        return response

    response = jsonify({"message": "CORS is working!"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    app.run(debug=True)
