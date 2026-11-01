from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "FreeFire Unified API (OB55+ Ready)",
        "endpoints": [
            "/get_player_personal_show?server=sg&uid=2081383145",
            "/get_player_stats?server=sg&uid=2081383145&gamemode=br&matchmode=RANKED",
            "/get_search_account_by_keyword?server=sg&keyword=ProGamer",
            "/check_banned?uid=2081383145"
        ]
    })

@app.route("/get_player_personal_show", methods=["GET"])
def get_player_personal_show():
    uid = request.args.get("uid", "").strip()
    server = request.args.get("server", "SG").upper()

    if not uid:
        return jsonify({"error": "Missing uid parameter"}), 400

    # Primary: PRINCE-lki Free Fire v1 API | Fallback: paulafredo glob-info2 API
    urls = [
        f"https://freefireinfo-zy9l.onrender.com/api/v1/player-profile?uid={uid}&server={server}&need_gallery_info=true&need_spark_info=true",
        f"https://glob-info2.vercel.app/info?uid={uid}"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200:
                data = r.json()
                if data and not data.get("error") and data.get("code") != "MAJOR_LOGIN_FAILED":
                    return jsonify(data)
        except Exception:
            continue

    return jsonify({"status": "error", "message": "All upstream profile nodes timed out or failed."}), 502

@app.route("/get_player_stats", methods=["GET"])
def get_player_stats():
    uid = request.args.get("uid", "").strip()
    server = request.args.get("server", "SG").upper()
    gamemode = request.args.get("gamemode", "br").lower()
    matchmode = request.args.get("matchmode", "CAREER").upper()

    if not uid:
        return jsonify({"error": "Missing uid parameter"}), 400

    url = f"https://freefireinfo-zy9l.onrender.com/api/v1/player-stats?uid={uid}&server={server}&gamemode={gamemode}&matchmode={matchmode}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

    return jsonify({"status": "error", "message": "Unable to fetch player stats."}), 502

@app.route("/get_search_account_by_keyword", methods=["GET"])
def get_search_account_by_keyword():
    keyword = request.args.get("keyword", "").strip()
    server = request.args.get("server", "SG").upper()

    if len(keyword) < 3:
        return jsonify({"error": "Keyword must be at least 3 characters"}), 400

    url = f"https://freefireinfo-zy9l.onrender.com/api/v1/search-players?keyword={keyword}&server={server}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

    return jsonify({"status": "error", "message": "Search failed."}), 502

@app.route("/check_banned", methods=["GET"])
def check_banned():
    uid = request.args.get("uid", "").strip()
    if not uid:
        return jsonify({"error": "Missing uid parameter"}), 400

    ban_url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}"
    ban_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "B6FksShzIgjfrYImLpTsadjS86sddhFH",
        "Referer": "https://ff.garena.com/en/support/"
    }
    try:
        r = requests.get(ban_url, headers=ban_headers, timeout=15)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)