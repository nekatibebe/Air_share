 INSA SUMMER CAMP DEPARTMENT OF CYBER SECURITY
SUBMITTED BY: FELEKE CHEKOLE GENETU
ACADEMIC YEAR: 2018 e.c


These are main concepts 
Architectural concepts and assumptions
  Zero-internet operational mode: the app can't rely on external clouds,databases, or public authorities. Everything 
must be handled locally in system memory(RAM).
Hostile network environment:state clearly that your threat model assumes an untrusted LAN/Hotspot. This means any device
connecting to your WI-FI is considered a potential attacker until proven otherwise.
2, core cryptographic primitive choices


🖥️ Slide 1: Title Slide
Slide Title: AirShare: Engineering a Hardened,
Zero-Internet Local File Vault
Subtitle: An Offline, Defense-in-Depth 
Storage Node for Hostile Networks
Presenter Information:Feleke Chekole 
Cybersecurity & Networking
INSA summer camp Project
Visual Anchor Ideas: Icon of a locked shield overlapping a Wi-Fi broadcasting antenna.
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
🖥️ Slide 4: Defensive Pillar 1 — Transport Layer Security
 Slide Title: Defeating Over-the-Air Packet Sniffing (Wireshark)
Bullet Points:

The Vulnerability: Cleartext credential and file harvesting via wireless monitoring tools running in promiscuous mode.
The Cryptographic Fix: On-the-fly execution of the Python cryptography primitive library upon booting.
Mechanism: Automatically generates an ephemeral 2048-bit RSA Private Key and a self-signed X.509 TLS 
 certificate in memory.
Security Control: Forces all client endpoints to communicate exclusively over a hardened, encrypted HTTPS pipeline.
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
🖥️ Slide 7: Defensive Pillar 4 — Session Management
Slide Title: Session Lifecycles & Cookie Hardening
Bullet Points:

Token Generation: Avoids predictable user IDs; handles tracking via high-entropy secrets.token_hex(16) values.
Cookie Configuration Flags:
 HttpOnly=True: Blocks client-side JavaScript execution environments from harvesting access tokens.
 SameSite=Strict & Secure=True: Prevents cross-domain ambient bleeding and binds transmissions strictly to HTTPS.
Sliding Inactivity Expiration: 
Automatically purges authentication records after 600 seconds (10 minutes) of idle timeout.
🖥️ Slide 8: Core API Mapping
Slide Title: Endpoint Matrix & Permissions Routing
Content Structure (Presented as a scannable table or clean list):
GET /login: Public path serving the encrypted authentication interface cards.
POST /login: Throttled endpoint validating credentials and issuing session cookies.
GET /: Protected directory exploration route that scans current subfolders.
POST /upload: Protected multipart handler injecting files safely to disk.
GET /view/<path>: Protected inline viewer routing content based on MIME types.
GET /download/<path>: Protected attachment pipe forcing direct file downloads.
🖥️ Slide 9: Core Security Trade-offs & Limitations
Slide Title: Engineering Candor: Constraints and Realities
Bullet Points:

The Local TLS Warning: Browsers display a warning flag on initial connection due to the self-signed nature of the certificate. 
 This is a mathematical reality of operating an authoritative node offline without global CA trust chains.
Volatile State Constraints: Session storage maps to local system memory (RAM). 
Restarting the Python backend completely drops active tokens, resulting in temporary service interruptions but optimizing data volatility.
The iOS Sandbox Obstacle: Senders and receivers running Apple devices function perfectly via Safari, 
but local system boundaries prevent downloading the app installer bundle itself offline.
🖥️ Slide 10: Conclusion & Core Takeaways
Slide Title: Project Summary & Key Learning Milestones
 Bullet Points:

 Project Deliverable: Successfully built a minimized, reliable, multi-layered security vault tailored for offline hotspot file delivery.
System Administration Mastery: Handled native environment packaging via Linux file hierarchy structures (/usr/local/bin/).
Practical Defense Application: Transformed common web application security principles (OWASP Top 10) into real-world code defensive lines.
Open for Questions: Thank you! Open for technical review or code demonstration.
