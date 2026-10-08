
# 1: SYSTEM SPECIFICATION & ADVANCED PROJECT RATIONALE


### 1.1 The Architecture of Untrusted Link-Layer Networks

In the design of modern file-sharing applications, engineering teams routinely offload security, access control, and identity mapping tasks to upstream infrastructure layers. When an application operates on a corporate network or across the worldwide web, it heavily relies on foundational trust assumptions built into external systems:

     [ Internet File App ] ──► (Public DNS Route) ──► (Let's Encrypt CA validation) ──► (OAuth Core Server)

These external abstractions include public Domain Name System (DNS) configurations for routing verification, public Certificate Authorities (like Let's Encrypt or DigiCert) to validate cryptographic signatures, and remote cloud identity providers (OAuth, OpenID Connect) to handle access control.

However, when you sever the link to the global internet, this entire trust pipeline breaks instantly. Offline data-sharing tools like Apple AirDrop, standard Xender, or basic HTTP server modules are built on a highly flawed security assumption: that local proximity equals trust.

Because these tools are physically limited to an offline Local Area Network (LAN) or a mobile hotspot radio footprint, developers often optimize them for convenience, skipping authentication and encryption layers entirely.

From an adversary's perspective, this creates an ideal exploit environment. The moment a wireless hardware chip transitions into an open Access Point (AP), it establishes a flat, non-isolated Layer 2 broadcast domain. Any network card within wireless propagation range can connect to the radio bands.

Without encryption, all data packets travel through the air as cleartext radio waves. Anyone running a passive monitor tool can capture files, intercept configuration arguments, and harvest active session data straight out of the air.
### 1.2 Architectural Constraints of Zero-Internet Environments

Building a secure tool under strict zero-internet constraints changes how you write software. You can no longer make simple API calls to third-party web services or rely on external packages that fetch updates over the net.

The application must be completely self-sufficient. This constraint means your code cannot connect to cloud engines to process user profiles, meaning authentication states must be generated and managed directly on the local machine.

Furthermore, you cannot rely on persistent, heavy external database engines like MySQL or PostgreSQL, which introduce installation overhead and expose the application to complex query injection risks. The system must operate efficiently using only a lightweight, minimal software footprint.

Every single security control—including tracking requests for rate limiting, verifying session states, and generating cryptographic keys—must happen completely inside volatile system memory (RAM). This isolation creates a rigid boundary: the application must act as its own security firewall, its own Certificate Authority, and its own real-time logging monitor, all while running on a device entirely cut off from the rest of the world.

### 1.3 Project Core Engineering Requirements

The AirShare Secure Node project was built to address these specific vulnerabilities by engineering a secure, self-contained file vault. It replaces the open, unencrypted design of standard file-sharing tools with a strict Zero-Trust paradigm. The application treats every connected client device as a potential threat until it proves its identity.

   The primary technical requirements for this project include:
                 
                 ┌──► 1. Transport Layer Security (In-Memory X.509 CA Signing)
                 ├──► 2. Local Namespace Discovery (Avahi mDNS System Engine) 
    Airshare core├──► 3. Identity Ingress Barriers (Secure Anti-XSS Login Gates)
                 ├──► 4. Anti-Scanning Firewalls (Sliding-Window Rate Limiting)
                 └──► 5. System Directory Isolation (Canonical Bound Jail)

1, Transport Layer Security: The tool must instantly encrypt all data over the local network using dynamically generated cryptographic keys, preventing anyone from sniffing packets over the air.

2, Local Namespace Discovery: It must publish a clean, easy-to-use local domain name without internet connection, removing the need for users to type long, confusing IP addresses.

3, Identity Ingress Barriers: The app must force client devices through a secure login screen, blocking unauthorized users from seeing the folder structure or files.

4, Anti-Scanning Firewalls: It must feature a built-in network throttle to block automated scanning tools (like GoBuster) and automated password crackers.

5, System Directory Isolation: The tool must use native file system hooks to let the host pick any directory to share at runtime, securely isolating the rest of the computer's hard drive from client access.
# 2: THREAT MODELING & DEEP ATTACK SURFACE DECONSTRUCTION

### 2.1 STRIDE Threat Analysis for Local Access Points
To properly secure the application, a formal security threat assessment was performed during the design phase using the STRIDE methodology. This analysis looks closely at how an attacker could exploit an open local hotspot network:

*Spoofing Identity:* Attackers on an open hotspot can easily spoof their network configurations or clone legitimate session tokens to gain unauthorized access. The app fixes this by generating unique, long, and unpredictable session tokens (secrets.token_hex(16)) and locking them behind strict browser security flags.

*Tampering with Data:* Attackers can intercept network packets to modify data mid-transit, or inject malicious path characters into URL parameters (like ?path=../../) to break out of the shared folder. The app stops this by enforcing strict path normalization boundaries on every request.

*Repudiation:* Without system logs, a user could perform malicious actions on the server without leaving a trace. The app integrates real-time console auditing that prints detailed security logs for every connection and file action.

*Information Disclosure (Sniffing):* This is the biggest threat on local networks. Anyone running a wireless card in monitoring mode can capture plain HTTP traffic and read files or passwords in cleartext. The app eliminates this by forcing mandatory TLS encryption (HTTPS) across all connections.

*Denial of Service (DoS):* Attackers can flood the server with automated fuzzing tools (like GoBuster) to exhaust system resources or crash the script. The app blocks this using a stateful, memory-isolated rate limiter that drops abusive connection paths instantly.

*Elevation of Privilege:* An unauthenticated user could attempt to bypass the login interface and access protected file downloads. The app stops this using an isolation gate that validates active session tokens before routing any protected data paths.
### 2.2 Exploitation Mechanics: Cleartext Radio Sniffing & Path Breakouts

Understanding the precise mechanics of a Cleartext Packet Capture Attack highlights why standard HTTP servers are highly dangerous on local networks. When a client device connects over plain HTTP, the browser packages all data—including the username, password, and files—into raw, unencrypted TCP segments.

If an attacker nearby places their wireless interface card into monitor mode using standard tools like airmon-ng and launches a network capture (tcpdump or Wireshark), they can intercept these radio packets straight out of the air:
      
    [ Client Phone ] ─── (Plain HTTP: User=Feleke Pass=Feleke@123) ───► [ Router ]
                                 │
                   ⚠️ (Adversary captures cleartext waves)
                                 │
                                 ▼
                     [ Wireshark Packet Dump ]
   Because the data is completely unencrypted, the attacker can use Wireshark's "Follow TCP Stream" feature to read the exact login credentials and reconstruct copies of transferred files directly from the captured bytes.

   A Directory Traversal Attack targets the server's input validation layer. If an application handles folder navigation by blindly combining path strings from the user (e.g., BASE_DIR + request.args.get('path')), an attacker can easily exploit this layout.

   By typing relative directory traversal characters like ../../../../etc/passwd into the URL query parameters, they can trick the operating system's file resolver. The system processes each .. step by climbing backward out of the shared directory, allowing the attacker to break out of the sandbox and read confidential system files from anywhere on the host's hard drive.
   ### 2.3 Attack Surface Minimization via Volatile State Memory

   To achieve a hardened security posture, the project purposefully avoids using any persistent storage databases or disk-cached tracking files. If an application writes session tokens or connection logs to temporary files on the hard drive, it expands its attack surface.

   An attacker who gains local user access could read those temporary files to steal active tokens, and if the server crashes unexpectedly, those session records remain on the disk as a forensic footprint.

   The AirShare Secure Node minimizes this risk by storing its entire state registry inside volatile system memory (RAM). Active session tokens, sliding rate-limit timestamps, and connection states live inside Python dictionary tables (active_sessions and rate_limit_records).

   Because this data is stored purely in RAM, it is completely volatile. The exact moment the server administrator terminates the script or stops the application, the operating system cleans the memory space. The session keys, logging histories, and tracking metrics evaporate instantly, leaving a zero-footprint trace on the physical disk.
   # 3: HARDWARE INTERFACING & LOCAL NETWORKING PRIMITIVES

   ### 3.1 Layer 2 Broadcast Domains and Virtual Interface Binding

   When your Linux desktop initializes a mobile hotspot or a local wireless network, the operating system's networking subsystem creates a dedicated virtual wireless interface card (typically labeled wlan0, ap0, or wlo1).

   The Linux kernel link-layer driver configures this interface to act as a Wireless Access Point (AP), broadcasting beacons that allow client devices to discover and connect to the radio band.

                      ┌──► Virtual Interface 'ap0' (Assigned IP 192.168.137.1)
                      ├──► DHCP Server (Hands out IPs 192.168.137.10 - 50)
    [ Kali Linux AP ] ├──► Local DNS Gateway (Maps local requests)
                      └──► Socket Listener (Binds to 0.0.0.0:9090)

  Once a client phone connects to this network, a local DHCP daemon (like dnsmasq or NetworkManager's internal routing hooks) automatically assigns it an IP address within a local subnet range (typically 192.168.137.x or 10.42.0.x). This sets up an isolated local network where your laptop sits at the center, acting as the primary gateway and authoritative router.

  ### 3.2 Socket Descriptors, Wildcard Binding (0.0.0.0), and OS VFS Interfacing
 
  To capture network traffic across this custom wireless interface, the Flask web framework uses an underlying network socket descriptor configured for wildcard binding:
  
     python
     app.run(host='0.0.0.0', port=9090)

Binding to the wildcard address 0.0.0.0 tells the operating system's network stack: "Do not restrict incoming connections to just one hardware interface. Open port 9090 and listen for incoming traffic on every single network card inside this machine."

This setup allows the app to simultaneously catch traffic coming from local loops (127.0.0.1), physical Ethernet cables, and the virtual hotspot interface card.

To bridge this web server to your computer's filesystem safely and dynamically, the app integrates with the operating system's Virtual File System (VFS) using a graphical UI window. When the script boots, it calls Python's native tkinter library:
             
     python
    root = tk.Tk()
    root.withdraw()
    BASE_DIR = filedialog.askdirectory()
The root.withdraw() line hides the tiny default Tkinter background window, while filedialog.askdirectory() opens a native desktop directory picker. This window hooks straight into the OS kernel, allowing the administrator to click and pick any folder on their drive.

The selected folder string is locked into a global constant variable (BASE_DIR), which acts as the absolute sandbox root boundary for all future file actions.
 ### 3.3 Multicast DNS (mDNS) & Local Hostname Publishing Mechanics
 Forcing users to type a raw local IP address (like https://192.168.137.251:9090) into their phone browser creates a clunky and difficult user experience. To fix this completely offline, the application uses Multicast DNS (mDNS), the underlying protocol behind Apple's Bonjour and Linux's Avahi systems.

 The script handles this local discovery mapping by launching an asynchronous background process that hooks straight into Linux's native Avahi daemon tool:

    python
    subprocess.Popen(["avahi-publish-address", "--no-reverse", "-a", "airshare.local", local_ip])
 The ensure_avahi_running() function uses system commands (systemctl is-active) to verify that the Avahi service is running on your system. If it is stopped, it automatically attempts to start it.

 Once verified, publish_local_hostname() spins up the avahi-publish-address process. This background daemon answers local network discoveries by broadcasting UDP packets across port 5353.

 When a phone browser asks, "Who owns the domain airshare.local?", your laptop's Avahi service intercepts the multicast packet and responds, "That domain belongs to my wireless card IP address." This allows users to connect to your file portal completely offline simply by typing https://airshare.local:9090 into their browsers.
 # 4: CRYPTOGRAPHIC ENGINEERING & PRIVATE CA ARCHITECTURE
 ### 4.1 Dual-Tier In-Memory Public Key Infrastructure (PKI)

 The core transport security of this project uses a custom, local Public Key Infrastructure (PKI) built directly into the initialization block using the Python cryptography library.

 Standard self-signed certificates generate a single temporary certificate for the server. However, modern smartphone browsers reject these basic standalone certificates, triggering security errors that can block the connection entirely.

 To solve this, the application implements an advanced Dual-Tier CA Architecture:
 
    [Generate Root CA ] ──► Compiles ca.private_key (4096-bit) + ca.pem Certificate
                               │
                               ▼
    [ Generate Server ]  ──► Compiles server_key (2048-bit) ──► Signed by Root CA ──► TLS Active
*The Root Certificate Authority (CA):* The script checks if a persistent local CA already exists. If missing, it generates a high-strength 4096-bit RSA Private Key and a root master certificate (ca.pem). This root certificate acts as your own personal offline trust authority.

 *The Server Certificate:* The script then creates a separate 2048-bit RSA Private Key for the active web server. It builds a downstream server certificate and signs it using the Root CA's master private key.

 This setup allows you to install your small ca.pem certificate onto a client device just once. From then on, the phone will seamlessly trust your file-sharing server without displaying any browser security warnings.
 ### 4.2 X.509 Certificate Structures & Cryptographic Assertions
 Building valid certificates offline requires configuring precise cryptographic properties inside the generate_self_signed_cert() function. When creating the Root CA, the script uses a CertificateBuilder pipeline to define critical properties:

    python
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
 Setting ca=True marks this certificate as an official, authoritative Certificate Authority that is allowed to sign downstream certificates. The script also configures explicit Key Usage flags to define what the certificate can be used for:

       python
    x509.KeyUsage(digital_signature=True, key_cert_sign=True, crl_sign=True, ...)
 Setting key_cert_sign=True gives the CA permission to sign server certificates, while crl_sign=True allows it to sign certificate revocation lists.

 The Root CA's validity dates are set to a 10-year window (days=3650), while the downstream server certificate is set to a 1-year expiration window (days=365). Finally, the certificates are signed using a secure SHA-256 cryptographic hash.












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


# These are main concepts 
* Architectural concepts and assumptions
  Zero-internet operational mode: the app can't rely on external clouds,databases, or public authorities. Everything 
must be handled locally in system memory(RAM).
Hostile network environment:state clearly that your threat model assumes an untrusted LAN/Hotspot. This means any device
connecting to your WI-FI is considered a potential attacker until proven otherwise.
2, core cryptographic primitive choices

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

