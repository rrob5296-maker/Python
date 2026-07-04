import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Set this in your host's environment variables, not in the code.
WEBHOOK_URL = "https://discord.com/api/webhooks/1522994693468848188/zlfm2886YfqZBHwaqB9EAfbfZKfXtS7SdPJ21WA0cbzAcgp5GLp4nO1tllYYaEfcfdyq"

def get_visitor_ip():
    # When hosted behind a proxy/load balancer, the real IP is in X-Forwarded-For.
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr

    
def get_reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return "no reverse DNS"


def log_to_discord(ip, path, user_agent):
    payload = {
        "content": (
            f"**New visit**\n"
            f"IP: `{ip}`\n"
            f"Reverse DNS: `{rdns}`\n"
            f"Path: `{path}`\n"
            f"User-Agent: `{user_agent}`"
        )
    }
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if r.status_code not in (200, 204):
            print(f"Discord webhook failed: {r.status_code} {r.text}")
    except requests.RequestException as e:
        print(f"Discord webhook error: {e}")

@app.route("/")
def home():
    ip = get_visitor_ip()
    rdns = get_reverse_dns(ip)
    log_to_discord(ip, rdns, request.path, request.headers.get("User-Agent", "unknown"))
    return render_template_string("""...your same HTML...""")

@app.route("/privacy")
def privacy():
    # Paste your existing policy here (or serve it from a template/file).
    return "<h1>Privacy Policy</h1><p>Your policy text goes here.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
