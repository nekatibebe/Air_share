## The real world problem i face and Need of developing Secured, offline, high-speed API based file Sharing tool
### 1,Internet dependency and High latency:
Sharing files often requires an active internet connection leading unnecessary slow transfer speeds, and heavy data consumption.
### 2,Storage limitation on mobile devices:
Managing large file directory on phones with limited storage requires a seamless way to preview and access files hosted on a PC without downloading them first
### 3, Privacy and network security risks:
Transmitting sensitive local data over public or cloud infrastructure exposes files to third-party interception and data leakage.
### 4, Lack of hardened local tools:
Existing offline utilities lack built-in security features like rate-limiting, encrypted transport, and input validation, and these types of security measures.
### 5,Data exposure over plain text protocols:
Traditional local file transfers(e.g HTTP, FTP, or unencrypted SMB) send data in clear text, making them vulnerable to packet sniffing and man-in-middle attack on shared WIFI networks.
## The proposed solutions for the tool
### 1, 100% Offline peer-to-peer Networks:
Operates over a local WIFI/Hotspot architecture without requiring active internet access.
### 2,High-Speed Transfer rates:
<img width="1062" height="1131" alt="Screenshot_20261007_211516_Chrome" src="https://github.com/user-attachments/assets/d65173a8-1d9b-47bd-a0a4-ab3684e75f0d" />

Achieves rapid local transfer speeds ranging from 5MB/S to 8MB/S, eliminating internet latency and bandwidth costs.
### 3, RSA-Based Encrypted Tunneling:
Utilizes RSA asymmetric encryption primitives to establish a secure, encrypted communication channel between host and clients.
### 4, Automated PKI and CA certificate Generation:
<img width="1528" height="42" alt="image" src="https://github.com/user-attachments/assets/0e9fe2b4-57f6-44d2-99fe-99208545c1ad" />

Programmatically generates on-the-fly CA Certificates and TLS keys, automatically configuring secure HTTPS connections for connected clients.
 and the client trusts and forces his device to trust
 <img width="591" height="1280" alt="image" src="https://github.com/user-attachments/assets/8b2314bc-670a-48dc-8103-83f6e2330126" />

## Defensive security pillars and system Hardening
### 1, Zero-configuration mDNS Resolution:
<img width="754" height="68" alt="Screenshot_2026-10-07_21-09-32" src="https://github.com/user-attachments/assets/10e1c8a8-a354-4fc5-aefd-cf7a1497e63e" />

Integrated mDNS/Avahi naming allowing clients to connect
via friendly hostnames(e.g .local domain) instead of typing new ip addresses.
### 2, IP based Sliding window rate limiter: 
<img width="1079" height="393" alt="Screenshot_20261007_211238_Chrome" src="https://github.com/user-attachments/assets/c5b8c1d4-eeb1-47ed-ba42-a2cb1bbaf865" />


Tracks incoming client request timestamps inside a rolling 60 second
window to block automated attack vectors.
<img width="1092" height="180" alt="Screenshot_2026-10-07_21-12-47" src="https://github.com/user-attachments/assets/a0e21616-5fe0-4ebc-a7e0-1099d9f626a6" />

### 3,Privileged Execution Safeguards:
<img width="770" height="180" alt="Screenshot_2026-10-07_21-08-44" src="https://github.com/user-attachments/assets/35659885-98f6-4791-8842-c5ff50b028df" />

Requires sudo authentication at startup to bind low-level system
networking services safely.
### 4,Authentication Gatekeeper: 
<img width="591" height="1280" alt="image" src="https://github.com/user-attachments/assets/5b4c6936-4b09-4a39-8021-3c80bb1a38b0" />

Features a dedicated login gateway to authenticate clients before granting file-
system access or download capabilities.
### 5,Path Traversal Isolation: 
<img width="1079" height="367" alt="image" src="https://github.com/user-attachments/assets/c1254977-d918-4f64-8ff4-869ef54e1ab1" />
Enforces strict path normalization(secure_target_path) to lock clients inside specified
host directories, preventing directory traversal attacks(../).

### 6,In-memory RAM state Databases: 
Stores active states and request metadata directly in volatile memory for
ultra-fast security processing without database overhead.

## System Architecture and workflow diagram
### 1, Network Initialization:
Host creates a local WI-FI Hotspot, and client devices connect directly without external internet access.
### 2, Host application setup:
Host launces the server; a GUI(Tkinter) promotes the host to select the target shared
directory.
<img width="1920" height="1080" alt="Screenshot_2026-10-06_20_34_12" src="https://github.com/user-attachments/assets/aef15c56-4629-4ff0-9ccc-d1497fbc3d0f" />

### 3, Service discovery and sudo binding: 
Request sudo privileges to initialize avahi-daemon for mDNS resolution,
matching the local ip address to .local domain name.
<img width="770" height="180" alt="Screenshot_2026-10-07_21-08-44" src="https://github.com/user-attachments/assets/98651c2c-9ca1-410c-aea5-65ab94cd2770" />

### 4, Secure client connection and Auth:
Displays a connection link for clients; clients install/trust the host’s CA certificate in their browser and access the HTTPS portal.
### 5, Access and storage operations:
Clients pass the login gateway to access the shared folder to stream, preview,download, or upload files securely within host-granted boundaries.
## Target use cases:Who needs this Tool?
### Healthcare institutions and Hospitals:
Enables doctors, radiologists, and administrative staff
to securely and medical imaging files(e.g X-rays, MRI scans) across departments without sending data over external networks.
### Banking and Financial Institutions: 
Facilitates high-security inter-office document sharing between
teller desks and management terminals while maintaining zero exposure to public cloud leaks or internet-based sniffing.
### Corporate Office Networks:
Allows inter-office computer to computer file exchange without overloading office
internet bandwidth, ensuring business documents remain strictly within local office premises.
### Air-Gapped and High-security Environments(e.g military comand posts, hospital MRI labs, banking vault): 
provides secure, offline file transfer for organization-critical operations where external internet connections
are restricted for compliance and privacy.

## Future enhancements and Scaling Roadmap
### Dynamic user Management and secure Auth:
Replace static credentials with a full sign-up/sign-in user registration system, storing hashed
passwords securely in a database(e.g., SQLite/PostgreSQL with bcrypt).
### Mesh Network Topology:
transition from a single Hotspot/Access Point model to a peer-to-peer Mesh Topology, extending file-sharing
coverage across unlimited geographical distances
through multi-hop node relaying.
### MIME/Byte-Level File Inspection:
Upgrade upload verification by inspecting ra
### Making it more user friendly:

# 🛡️ AirShare: Hardened, Zero-Internet Local File Vault

An offline, defense-in-depth local file-sharing server engineered to operate securely over Local Area Networks (LAN) and Wireless Access Points (Hotspots) without an internet connection.

---
 # INSA SUMMER CAMP DEPARTMENT OF CYBER SECURITY PROJECT
SUBMITTED BY: FELEKE CHEKOLE GENETU  
ACADEMIC YEAR: 2018 e.c

---
# outlines
1. Architectural concepts.................................................1
2. 
# These are main concepts 
* Architectural concepts and assumptions
  Zero-internet operational mode: the app can't rely on external clouds,databases, or public authorities. Everything 
must be handled locally in system memory(RAM).
Hostile network environment:state clearly that your threat model assumes an untrusted LAN/Hotspot. This means any device
connecting to your WI-FI is considered a potential attacker until proven otherwise.
2, core cryptographic primitive choices

---

🖥️ Slide 1: Title Slide
Slide Title: AirShare: Engineering a Hardened,
Zero-Internet Local File Vault
Subtitle: An Offline, Defense-in-Depth 
Storage Node for Hostile Networks
Presenter Information:Feleke Chekole 
Cybersecurity & Networking
INSA summer camp Project
Visual Anchor Ideas: Icon of a locked shield overlapping a Wi-Fi broadcasting antenna.

---

🖥️ Slide 2: Project Scope & Problem 
Statement
Slide Title: The Problem: Unsecured Offline Sharing
Bullet Points:

The Scenario: Deploying file-sharing tools
over local Wi-Fi Hotspots without global internet dependencies.
The Flaw: Industry tools prioritize "open convenience." Standard localized sharing transfers cleartext 
 data over unencrypted HTTP.
The Threat Model: The local wireless footprint is assumed to be a hostile environment. 
Any connected client can eavesdrop or attempt malicious input manipulation.
The Objective: Build a lightweight, cross-platform file server that enforces zero-trust web application 
 security completely offline.

---

🖥️ Slide 3: Architectural Overview
 Slide Title: System Architecture & Design
Bullet Points:

 Framework Stack: Built on an asynchronous Python Flask micro-engine with zero external database dependencies.
Volatile Memory State: All user tokens, sliding timers, and active session states 
live entirely in system RAM.
Zero-Client Installation: Senders and receivers interact natively 
 through standard web browsers (Safari,Chrome ,firefox ).
Dynamic Binding: Utilizes Tkinter UI file dialogs to allow the server host to target and switch isolation folders
 dynamically at runtime.

---

🖥️ Slide 4: Defensive Pillar 1 — Transport Layer Security
 Slide Title: Defeating Over-the-Air Packet Sniffing (Wireshark)
Bullet Points:

The Vulnerability: Cleartext credential and file harvesting via wireless monitoring tools running in promiscuous mode.
The Cryptographic Fix: On-the-fly execution of the Python cryptography primitive library upon booting.
Mechanism: Automatically generates an ephemeral 2048-bit RSA Private Key and a self-signed X.509 TLS 
 certificate in memory.
Security Control: Forces all client endpoints to communicate exclusively over a hardened, encrypted HTTPS pipeline.

---

🖥️ Slide 5: Defensive Pillar 2 — Request Throttling
Slide Title: Mitigating Automated Scanners & Brute-Force
Bullet Points:
 The Vulnerability: Content fuzzing via tools like GoBuster / DirBuster and administrative credential
  cracking via automation.
The Implementation: An in-memory, IP-tracked sliding-window rate limiter hooks directly into @app.before_request.
Rigid Threshold Barriers:
 /login Endpoint: Strictly capped at a maximum of 5 POST attempts per minute.
 General Subdirectory Content: Capped at 45 requests per minute per client IP.
Result: Triggers an immediate HTTP 429 Too Many Requests block, dropping malicious threads before resource consumption occurs.

---

🖥️ Slide 6: Defensive Pillar 3 — Input Sanitization
 Slide Title: Neutralizing Directory Traversal & XSS
Bullet Points:
 Path Traversal Attack Vector: Malicious path arguments (e.g., ?path=../../etc/shadow) injected to break past
 folder isolation barriers.
Path Fix: os.path.normpath analyzes the absolute path structure recursively, enforcing a rigid boundary check: 
 .startswith(BASE_DIR). Any violation drops with a 403 Forbidden log.
Cross-Site Scripting (XSS) Vector: Maliciously named file uploads (e.g., <script>alert(1)</script>.png) 
 attempting client-side script execution.
Sanitization Fix: Enforces html.escape() to sanitize file data representations into inert text strings before 
 browser rendering.

---

🖥️ Slide 7: Defensive Pillar 4 — Session Management
Slide Title: Session Lifecycles & Cookie Hardening
Bullet Points:

Token Generation: Avoids predictable user IDs; handles tracking via high-entropy secrets.token_hex(16) values.
Cookie Configuration Flags:
 HttpOnly=True: Blocks client-side JavaScript execution environments from harvesting access tokens.
 SameSite=Strict & Secure=True: Prevents cross-domain ambient bleeding and binds transmissions strictly to HTTPS.
Sliding Inactivity Expiration: 
Automatically purges authentication records after 600 seconds (10 minutes) of idle timeout.

---

🖥️ Slide 8: Core API Mapping
Slide Title: Endpoint Matrix & Permissions Routing
Content Structure (Presented as a scannable table or clean list):
GET /login: Public path serving the encrypted authentication interface cards.
POST /login: Throttled endpoint validating credentials and issuing session cookies.
GET /: Protected directory exploration route that scans current subfolders.
POST /upload: Protected multipart handler injecting files safely to disk.
GET /view/<path>: Protected inline viewer routing content based on MIME types.
GET /download/<path>: Protected attachment pipe forcing direct file downloads.

---

🖥️ Slide 9: Core Security Trade-offs & Limitations
Slide Title: Engineering Candor: Constraints and Realities
Bullet Points:

The Local TLS Warning: Browsers display a warning flag on initial connection due to the self-signed nature of the certificate. 
 This is a mathematical reality of operating an authoritative node offline without global CA trust chains.
Volatile State Constraints: Session storage maps to local system memory (RAM). 
Restarting the Python backend completely drops active tokens, resulting in temporary service interruptions but optimizing data volatility.
The iOS Sandbox Obstacle: Senders and receivers running Apple devices function perfectly via Safari, 
but local system boundaries prevent downloading the app installer bundle itself offline.

---

🖥️ Slide 10: Conclusion & Core Takeaways
Slide Title: Project Summary & Key Learning Milestones
 Bullet Points:

 Project Deliverable: Successfully built a minimized, reliable, multi-layered security vault tailored for offline hotspot file delivery.
System Administration Mastery: Handled native environment packaging via Linux file hierarchy structures (/usr/local/bin/).
Practical Defense Application: Transformed common web application security principles (OWASP Top 10) into real-world code defensive lines.
Open for Questions: Thank you! Open for technical review or code demonstration.

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

