# 🛡️ AirShare: Hardened, Zero-Internet Local File Vault

An offline, defense-in-depth local file-sharing server engineered to operate securely over Local Area Networks (LAN) and Wireless Access Points (Hotspots) without an internet connection.

---

## 📋 Executive Summary
The **AirShare Secure Node** is a minimized, security-hardened file-sharing framework built natively in Python using the Flask micro-framework. Developed as a comprehensive cybersecurity portfolio capstone, this tool transitions file-transfer utilities from open convenience to a **Zero-Trust paradigm**. 

Assuming the local hotspot radio range is entirely hostile and untrusted, the application integrates ephemerally generated **Transport Layer Security (TLS)**, memory-isolated **sliding-window rate-limiting**, and multi-layered **input validation barriers** to protect the host machine against wireless sniffing, path traversal exploits, and automated directory fuzzing (e.g., GoBuster).

---
---

## 🔄 System Architecture & Data Workflow
The system operates as an authenticated client-server pipeline entirely contained within a local radio footprint. The diagram below illustrates how a zero-trust handshake is established offline:

```text
 [ Phone Client Browser ]                     [ Local Hotspot ]                [ Kali Linux Host Server ]
            │                                         │                                    │
            │ 1. Navigates to https://<IP>:9090 ─────►│                                    │
            │ ◄───────────────────────────────────────┼───────── 2. Serves Secure Login Page
            │                                         │                                    │
            │ 3. Submits Username & Password ────────►│                                    │
            │ ◄───────────────────────────────────────┼───────── 4. Validates & Issues Cookie Token
            │                                         │                                    │
            │ 5. Requests File Stream (GET/POST) ────►│                                    │
            │            [ RATE LIMIT GATE ]          │                                    │
            │            [ BOUNDARY CHECK  ] ─────────┼────────────────────────┐           │
            │                                         │                        │ (Inspects Path/IP)
            │                                         │ ◄──────────────────────┘           │
            │ ◄───────────────────────────────────────┼───────── 6. Streams Data Payload / 429 Error
```

### Flow Checklist:
1. **Ingress Route:** Client initiates an encrypted TLS handshake via browser to the dynamically assigned host IP.
2. **Access Gate:** Request passes through the `before_request` IP sliding-window tracker to verify rate thresholds.
3. **Authentication:** User submits credentials over HTTPS; server issues a cryptographically secure, `HttpOnly`, `Secure` cookie session token.
4. **Data Isolation Check:** File requests dynamically execute a canonical normalization step (`os.path.normpath`) checking structural parameters against the parent root folder bounds before execution.

---

## 📸 System UI Screenshots & Visual Walkthrough

### A. Core Control Console (Host Dashboard)
When you launch the tool natively from your terminal, it will automatically look up your active network interface card configurations and output an easy-to-read connection pane.

![Kali Linux Terminal Host Server](images/screenshot_terminal.png)

### B. Device Authentication Layer (Client Ingress View)
When a device connects to your hotspot and opens the web link, they are immediately stopped by an encrypted login screen. Standard routing access is completely disabled until credentials match.

![Secure Mobile Login Interface](images/screenshot_mobile.png)

### C. Authenticated File Explorer Dashboard
Once verified, the mobile browser transforms into a lightweight file explorer, allowing users to recursively look inside directories, stream previews natively via "Open," or download records cleanly to disk.

![Secure Dynamic File Index](images/screenshot_explorer.png)

---

## 🔒 Cybersecurity Threat Model & Defensive Pillars

### 1. Transport Encryption (Mitigating Over-the-Air Packet Sniffing)
* **The Vector:** In typical offline hotspot deployments, unencrypted cleartext HTTP traffic can be intercepted by any nearby network interface card operating in promiscuous mode (using tools like Wireshark).
* **The Defense:** On system boot, the application utilizes the native Python `cryptography` library to generate a temporary **2048-bit RSA Private Key** and an **ephemeral X.509 TLS certificate** directly inside system RAM. 
* **Result:** All credentials, cookies, and file payloads are transmitted over a hardened **HTTPS** pipeline, rendering wireless captures unreadable.

### 2. Request Throttling (Mitigating GoBuster, Fuzzing & Brute-Force)
* **The Vector:** Attackers can run automated tools like GoBuster/DirBuster to discover sensitive directory structures or run password brute-forcers against authentication paths.
* **The Defense:** A sliding-window rate-limiting gate intercepts ingress network traffic at the global routing layer (`@app.before_request`). It logs client behaviors directly against their source hardware IP string (`request.remote_addr`):
  * **`/login` (POST Requests):** Restricted to a maximum of **5 attempts per minute**.
  * **General Storage Directories:** Restricted to **45 total requests per minute**.
* **Result:** Automated threat signatures trigger an immediate **`HTTP 429 Too Many Requests`** block, dropping connections before server system resource starvation occurs.

### 3. Absolute Boundary Isolation (Mitigating Path Traversal Actions)
* **The Vector:** Attackers can inject traversal variables into HTTP query strings (e.g., `?path=../../etc/shadow`) to break past app directory boundaries.
* **The Defense:** The application routes filesystem checks through a canonical normalization function:
  ```python
  base_norm = os.path.normpath(BASE_DIR)
  target_norm = os.path.normpath(os.path.join(base_norm, rel_path))
  if not target_norm.startswith(base_norm):
      abort(403)
  ```
* **Result:** If an evaluated query path steps out of the designated workspace border, the server triggers an intentional runtime alert event and forces an **`HTTP 403 Forbidden`** drop.

### 4. Cross-Site Scripting (XSS) Mitigation
* **The Defense:** File inventory item rendering maps variables through `html.escape()`. If a malicious client uploads a file named `<script>alert(1)</script>.png`, the string is sanitized into inert text entities before browser compilation, neutralizing arbitrary DOM injection scripts.

---

## 🛠️ Installation & Global Execution on Linux

### 1. Provision Dependencies
Install the required system cryptographic primitives via your terminal:
```bash
pip install cryptography flask
```

### 2. Make it a Global System Command (CLI Integration)
Transform the raw Python script into a natively executable system utility (similar to `nmap` or `wireshark` syntax):
```bash
# 1. Inject the necessary Python shebang line
sed -i '1i#!/usr/bin/env python3' app.py

# 2. Relocate the binary to the global path matrix
sudo cp app.py /usr/local/bin/airshare

# 3. Provision absolute execution permissions
sudo chmod +x /usr/local/bin/airshare
```

Now, you can drop into any terminal shell directory and spin up the node globally by typing a single word:
```bash
airshare
```

---

## 📡 Deployment & Verification Checklist

1. **Initialize Hotspot:** Enable your Linux wireless mobile hotspot engine. Connect a client mobile device to the network footprint.
2. **Launch Server:** Execute `airshare` from the terminal and choose your target base share folder from the pop-up GUI picker.
3. **Connect Client:** Open the browser on your phone and go to the custom `https://` address link displayed on your server console.
4. **Bypass Local CA Flag:** Since the certificate is self-signed offline without a public trust chain, click *Advanced -> Proceed* to enter the encrypted channel.
5. **Simulate a Attack Scenario:** Open a second shell window on your Kali machine and target your server using GoBuster to watch the automated blocking system activate:
   ```bash
   gobuster dir -u https://127.0.0.1:9090 -w /usr/share/wordlists/dirb/common.txt -k
   ```
   *Note the console outputs mapping out the `HTTP 429` connection rejections.*

---

## 🎓 Academic Presentation Slide Summary
* **Slide 1:** Project Title & Scope (The Hostile LAN Environment Challenge)
* **Slide 2:** Core Framework Constraints (Asynchronous Flask, In-Memory Memory Mapping)
* **Slide 3:** Pillar 1 Validation (TLS Encryption Mechanics against Over-The-Air Sniffers)
* **Slide 4:** Pillar 2 Validation (IP Sliding Window Constraints against GoBuster Engines)
* **Slide 5:** Pillar 3 Validation (Directory Escape Sanitization via Path Normalization)
* **Slide 6:** Pillar 4 Validation (Secure Cookie Flag Enforcements: HttpOnly & SameSite)
* **Slide 7:** System Matrix Map (Endpoint permissions matrix)
* **Slide 8:** Production Trade-offs (Self-Signed Certificates & Browser UI Alerts)
* **Slide 9:** Execution Strategy (Transforming code into custom global terminal tools)
* **Slide 10:** Analytical Summary (Conclusion, Vulnerability Matrix Logs, QA)

