#!/usr/bin/env python3
import os
import sys
import ipaddress
import socket
import psutil
import mimetypes
import secrets
import atexit
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import filedialog
from flask import Flask, request, render_template_string, send_from_directory, abort, make_response, redirect
# Cryptography primitives to generate the self-signed TLS certificate
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
# INITIALLY THE HOST SELECTS THE FOLDER HE WANTS TO SHARE
root = tk.Tk()
root.withdraw()
print("Please select the BASE folder you want to share...")
BASE_DIR = filedialog.askdirectory(title="Select Secure Base Share Folder")
if not BASE_DIR:
    print("❌ [CRITICAL] No folder selected. Exiting server.")
    sys.exit()
print(f"Isolation barrier locked around: {BASE_DIR}")
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
# CREDENTIALS OF THE USER TO AUTHENTICATE
AUTH_USER = "Feleke"
AUTH_PASS = "Feleke@123"
# SECURITY STATE DATABASES (In-Memory RAM Tables)
active_sessions = {} 
SESSION_TIMEOUT = 600   # 10 Minutes in seconds
rate_limit_records = {} # Format: { ip: [timestamp1, timestamp2, ...] }
# IP-BASED RATE LIMITING ENGINE
# This stops GoBuster fuzzing and password brute-forcing at the routing layer
def is_rate_limited(ip_address, max_requests=10, window_seconds=60):
    current_time = time.time()
    if ip_address not in rate_limit_records:
        rate_limit_records[ip_address] = [current_time]
        return False
    # Sliding window filter: Remove requests older than the time window
    timestamps = rate_limit_records[ip_address]
    rate_limit_records[ip_address] = [t for t in timestamps if current_time - t < window_seconds]
    if len(rate_limit_records[ip_address]) >= max_requests:
        return True
    rate_limit_records[ip_address].append(current_time)
    return False
#HARDENED HTML LAYOUTS (Login Page and Document Explorer)
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure AirShare - Authentication</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 100%; max-width: 360px; }
        h2 { text-align: center; margin-bottom: 24px; color: #38bdf8; }
        input { width: 93%; padding: 12px; margin-bottom: 16px; border: 1px solid #334155; border-radius: 6px; background: #0f172a; color: white; font-size: 15px; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; width: 100%; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0369a1; }
        .error { color: #f87171; font-size: 14px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🔒 Vault Guard (HTTPS)</h2>
        {% if error %} <div class="error">{{ error }}</div> {% endif %}
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required autocomplete="off">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn">Authenticate Device</button>
        </form>
    </div>
</body>
</html>
"""

EXPLORER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure AirShare Explorer</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 600px; margin: 20px auto; padding: 0 10px; background: #f8fafc; color: #0f172a; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer; }
        .logout-link { float: right; color: #ef4444; text-decoration: none; font-weight: bold; font-size: 14px; }
        .back-btn { background: #64748b; color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 15px; }
        ul { list-style: none; padding: 0; }
        .item { display: flex; justify-content: space-between; background: white; padding: 12px 15px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); align-items: center; }
        .folder-link { color: #0284c7; text-decoration: none; font-weight: bold; }
        .actions a { font-weight: bold; text-decoration: none; margin-left: 12px; }
        .view-link { color: #3b82f6; }
        .download-link { color: #10b981; }
        .current-path { font-family: monospace; background: #e2e8f0; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
    </style>
</head>
<body>
    <a href="/logout" class="logout-link">⚠️ Terminate Session (Logout)</a>
    <h2>🛡️ Secure Vault Active</h2>
    <p>Directory Isolation Path: <span class="current-path">/{{ relative_path }}</span></p>
    
    {% if relative_path %}
        <a class="back-btn" href="{{ url_for('home', path=parent_path) }}">⬅️ Back</a>
    {% endif %}
    
    <div class="card">
        <h3>Upload File Securely</h3>
        <form method="POST" action="{{ url_for('upload', path=relative_path) }}" enctype="multipart/form-data">
            <input type="file" name="my_file" required style="margin-bottom: 15px; display: block; width: 100%;">
            <button type="submit" class="btn">Upload to Current Subdirectory</button>
        </form>
    </div>

    <h3>Contents</h3>
    <ul>
        {% for folder in folders %}
            <li class="item">
                <a class="folder-link" href="{{ url_for('home', path=relative_path ~ folder ~ '/') }}">📁 {{ folder }}</a>
                <span style="color: #64748b; font-size: 12px;">Subfolder</span>
            </li>
        {% endfor %}

        {% if not folders and not files %}
            <p style="color: #64748b; text-align: center;">Directory is empty.</p>
        {% endif %}
        
        {% for file in files %}
            <li class="item">
                <span style="word-break: break-all; max-width: 60%;">📄 {{ file }}</span>
                <div class="actions">
                    <a class="view-link" href="{{ url_for('view_file', filepath=relative_path ~ file) }}" target="_blank">Open</a>
                    <a class="download-link" href="{{ url_for('download_file', filepath=relative_path ~ file) }}" download>Download</a>
                </div>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
"""
# 🛡️ INTERCEPT AND APPLY GLOBAL RATE LIMITS BEFORE PROCESSING REQUESTS
@app.before_request
def global_rate_limiting_gate():
    client_ip = request.remote_addr
    # Severe limit configuration on sensitive authentication paths to kill brute-forces
    if request.path == '/login' and request.method == 'POST':
        if is_rate_limited(client_ip, max_requests=5, window_seconds=60):
            print(f"🛑 [RATE LIMIT TRIGGERED] Brute-force block executed against IP: {client_ip}")
            return abort(429, "Too Many Login Attempts. Throttling request for 60 seconds.")
    # Standard limit configuration for overall asset/route fuzzing (GoBuster protection)
    else:
        if is_rate_limited(client_ip, max_requests=45, window_seconds=60):
            print(f"🛑 [RATE LIMIT TRIGGERED] Content enumeration block executed against IP: {client_ip}")
            return abort(429, "Rate limit exceeded. Automated scanning signatures detected.")
#  INPUT VALIDATION & PATH TRAVERSAL MITIGATION
def secure_target_path(rel_path):
    base_norm = os.path.normpath(BASE_DIR)
    target_norm = os.path.normpath(os.path.join(base_norm, rel_path))
    if not target_norm.startswith(base_norm):
        print(f"🚨 [ALERT] PATH TRAVERSAL ATTEMPT BLOCKED: Client tried escaping to {target_norm}")
        abort(403, "Security Violation: Directory Traversal Prohibited.")
    return target_norm
# AUTOMATED SESSION EXPIRATION VERIFIER
def verify_session():
    token = request.cookies.get('session_id')
    if not token or token not in active_sessions:
        return False
    session_data = active_sessions[token]
    current_time = time.time()
    if current_time - session_data['last_activity'] > SESSION_TIMEOUT:
        print(f"⏱️ [SECURITY] Session token {token[:8]}... expired due to timeout rules.")
        active_sessions.pop(token, None)
        return False
    session_data['last_activity'] = current_time
    return True
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        passwd = request.form.get('password')
        if user == AUTH_USER and passwd == AUTH_PASS:
            token = secrets.token_hex(16)
            active_sessions[token] = {'username': user, 'last_activity': time.time()}
            print(f"🔑 [AUTH SUCCESS] Session issued for active token: {token[:8]}...")
            response = make_response(redirect('/'))
            response.set_cookie('session_id', token, httponly=True, samesite='Strict', secure=True)
            return response
        else:
            print(f"⚠️ [AUTH FAILURE] Invalid login attempt with username: '{user}' from IP: {request.remote_addr}")
            return render_template_string(LOGIN_PAGE, error="Invalid Username or Password")
    return render_template_string(LOGIN_PAGE,error=None)
@app.route('/logout')
def logout():
    token = request.cookies.get('session_id')
    active_sessions.pop(token, None)
    response = make_response(redirect('/login'))
    response.set_cookie('session_id', '', expires=0)
    print("🔒 [SECURITY] Session explicitly killed by client request.")
    return response
@app.route('/')
def home():
    if not verify_session():
        return redirect('/login')
    rel_path = request.args.get('path', '').strip('/')
    if rel_path:
        rel_path += '/'
    target_dir = secure_target_path(rel_path)
    if not os.path.exists(target_dir):
        return "Target node directory missing.", 404
    parent_path = ''
    parts = rel_path.strip('/').split('/') if rel_path else []
    if len(parts) > 1:
        parent_path = '/'.join(parts[:-1]) + '/'
    all_items = os.listdir(target_dir)
    folders = []
    files = []
    for item in all_items:
        full_item_path = os.path.join(target_dir, item)
        if os.path.isdir(full_item_path):
            folders.append(item)
        elif os.path.isfile(full_item_path):
            files.append(item)
    folders.sort()
    files.sort()
    return render_template_string(
        EXPLORER_PAGE, folders=folders, files=files,
        relative_path=rel_path, parent_path=parent_path
    )
@app.route('/upload', methods=['POST'])
def upload():
    if not verify_session():
        return abort(401, "Session Expired.")
    rel_path = request.args.get('path', '').strip('/')
    target_dir = secure_target_path(rel_path)
    if 'my_file' not in request.files:
        return f'alert("No file chosen"); window.location="/?path={rel_path}";'
    file = request.files['my_file']
    if not file.filename:
        return f'alert("Empty filename"); window.location="/?path={rel_path}";'
    filename = os.path.basename(file.filename)
    file.save(os.path.join(target_dir, filename))
    print(f"🔒 [AUDIT] Inbound upload stream saved into filesystem sandbox: {filename}")
    return f'alert("Secure file uploaded!"); window.location="/?path={rel_path}";'
@app.route('/view/<path:filepath>')
def view_file(filepath):
    if not verify_session():
        return redirect('/login')
    target_file = secure_target_path(filepath)
    if not os.path.isfile(target_file):
        return "Target component not found.", 404
    return send_from_directory(os.path.dirname(target_file), os.path.basename(target_file),
                               mimetype=mimetypes.guess_type(target_file)[0])
@app.route('/download/<path:filepath>')
def download_file(filepath):
    if not verify_session():
        return redirect('/login')
    target_file = secure_target_path(filepath)
    if not os.path.isfile(target_file):
        return "Target entry missing.", 404
    return send_from_directory(os.path.dirname(target_file), os.path.basename(target_file),
                               as_attachment=True)
def generate_self_signed_cert(ca_path='ca.pem', ca_key_path='ca_key.pem', cert_path='cert.pem', key_path='key.pem'):
    """Generate a local CA (if missing) and a server certificate signed by that CA.
    Saves: ca.pem, ca_key.pem, cert.pem, key.pem. Returns (ca_created:bool, ca_path:str).
    """
    ca_created = False
    local_ip = get_local_ip()
    # Load existing CA if present
    if os.path.exists(ca_path) and os.path.exists(ca_key_path):
        with open(ca_key_path, 'rb') as f:
            ca_private_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(ca_path, 'rb') as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        print("🔁 [CERT] Reusing existing local CA (ca.pem)")
    else:
        # Create a new CA
        ca_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        ca_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AirShare Local CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "AirShare Local CA"),
        ])
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_subject)
            .issuer_name(ca_subject)
            .public_key(ca_private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                key_cert_sign=True,
                crl_sign=True,  # <--- ADD THIS PARAMETER
                data_encipherment=False,
                content_commitment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )
            .sign(ca_private_key, hashes.SHA256())
        )
        with open(ca_path, 'wb') as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        with open(ca_key_path, 'wb') as f:
            f.write(ca_private_key.private_bytes(serialization.Encoding.PEM,
                                                 serialization.PrivateFormat.TraditionalOpenSSL,
                                                 serialization.NoEncryption()))
        os.chmod(ca_key_path, 0o600)
        ca_created = True
        print("✅ [CERT] Created new local CA: ca.pem (trust this on clients to avoid browser warnings)")

    # Create server key and certificate signed by the CA
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AirShare Secure Node"),
        x509.NameAttribute(NameOID.COMMON_NAME, "airshare.local"),
    ])

    san_list = [
        x509.DNSName("airshare.local"),
        x509.DNSName("*.airshare.local"),
        x509.DNSName("localhost"),
    ]
    try:
        san_list.append(x509.IPAddress(ipaddress.ip_address(local_ip)))
    except Exception:
        pass
    san_list.append(x509.IPAddress(ipaddress.ip_address("127.0.0.1")))

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(san_list), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_private_key, hashes.SHA256())
    )
    with open(cert_path, 'wb') as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, 'wb') as f:
        f.write(server_key.private_bytes(serialization.Encoding.PEM,
                                         serialization.PrivateFormat.TraditionalOpenSSL,
                                         serialization.NoEncryption()))
    os.chmod(key_path, 0o600)
    return ca_created, ca_path
def get_local_ip():
    # Let the routing table choose the LAN interface instead of selecting the
    # first non-loopback address (which may be a VPN, tether, or container).
    route_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        route_probe.connect(("192.0.2.1", 80))
        routed_ip = route_probe.getsockname()[0]
        if routed_ip != "0.0.0.0" and not routed_ip.startswith("127."):
            return routed_ip
    except OSError:
        pass
    finally:
        route_probe.close()

    interfaces = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()
    preferred = ("wlan", "wifi", "wireless", "eth", "en")
    candidates = []
    for interface_name, addresses in interfaces.items():
        stats = interface_stats.get(interface_name)
        if not stats or not stats.isup or interface_name.lower() == "lo":
            continue
        for addr in addresses:
            if addr.family != socket.AF_INET or addr.address.startswith("127.") or addr.address == "0.0.0.0":
                continue
            priority = 0 if any(tag in interface_name.lower() for tag in preferred) else 1
            candidates.append((priority, addr.address))
    if candidates:
        candidates.sort()
        return candidates[0][1]
    raise RuntimeError("No active non-loopback IPv4 address is available for the server.")

def publish_local_hostname(local_ip):
    publisher = shutil.which("avahi-publish-address")
    if not publisher:
        print("⚠️ [mDNS] avahi-publish-address is unavailable; use the IP address instead.")
        return False
    process = subprocess.Popen(
        [publisher, "--no-reverse", "-a", "airshare.local", local_ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(0.5)
    if process.poll() is not None:
        _, error = process.communicate()
        print(f"⚠️ [mDNS] Could not publish airshare.local: {error.strip() or 'Avahi exited unexpectedly.'}")
        return False

    def stop_publisher():
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    atexit.register(stop_publisher)
    print("✅ [mDNS] Published airshare.local on the local network.")
    return True
def print_ca_install_instructions(ca_path):
    """Print platform-specific instructions to trust the generated CA certificate."""
    abs_path = os.path.abspath(ca_path)
    print("\n=== To avoid browser TLS warnings, install the generated CA certificate on client machines: ===")
    print(f"CA file: {abs_path}\n")
    print("Linux (Debian/Ubuntu):")
    print(f"  sudo cp {abs_path} /usr/local/share/ca-certificates/airshare_ca.crt")
    print("  sudo update-ca-certificates")
    print("macOS (system-wide, requires sudo):")
    print(f"  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain {abs_path}")
    print("Windows (PowerShell as Administrator):")
    print(f"  certutil -addstore -f Root {abs_path}")
    print("Firefox (per-profile): Open Preferences → Privacy & Security → View Certificates → Authorities → Import and select the CA file and trust it for websites.")
    print("Alternatively, use mkcert (https://github.com/FiloSottile/mkcert) to automate creating and trusting local certificates.")
    print("=====================================================================\n")
def insure_avahi_running():
    # check if avahi daemon is installed
    if not shutil.which("avahi-daemon"):
        print("[mDNS Warning] avahi daemon is not installed on this system.")
        return False
    # check if the daemon is currently active
    status_check = subprocess.run(
        ["systemctl", "is-active", "--quiet", "avahi-daemon"],
        capture_output=True,
        text=True
    )
    if status_check.returncode == 0:
        print("[mDNS] avahi-daemon is already running.")
        return True
    # Attempt to start the service
    print("[mDNS] Starting avahi daemon ...")
    try:
        subprocess.run(["sudo", "systemctl", "start", "avahi-daemon"], check=True)
        print("[mDNS] avahi-daemon started successfully.")
        return True
    except subprocess.CalledProcessError:
        print("[mDNS Error] Failed to start avahi-daemon. Ensure you run with root privileges.")
        return False
if __name__ == '__main__':
    local_ip = get_local_ip()
    target_port = 9090
    # start the daemon first
    insure_avahi_running()
    hostname_published = publish_local_hostname(local_ip)
    ca_created, ca_path = generate_self_signed_cert()
    # Print instructions so the operator can install the CA into client trust stores
    print_ca_install_instructions(ca_path)
    if hostname_published:
        print(f"👉 Target Connection: https://airshare.local:{target_port}")
    print(f"👉 IP connection: https://{local_ip}:{target_port}")
    app.run(host='0.0.0.0', port=target_port, ssl_context=('cert.pem', 'key.pem'))
