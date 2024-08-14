import time
import digitalio
from board import *
import board
import pwmio
from adafruit_debouncer import Debouncer
import wifi
import socketpool
import secrets
from adafruit_httpserver import Server, Request, Response, POST
import ipaddress
import supervisor

# Sleep at the start to allow the device to be recognized by the host computer
time.sleep(0.5)

# Turn off automatically reloading when files are written to the Pico
supervisor.runtime.autoreload = False

button1_pin = digitalio.DigitalInOut(board.GP22)
button1_pin.pull = digitalio.Pull.UP
button1 = Debouncer(button1_pin)

#### Misc functions ####
def getProgrammingStatus():
    # Check GP0 for setup mode
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return progStatus

def runScript(file):
    try:
        with open(file, "r", encoding='utf-8') as f:
            script_content = f.read()
        exec(script_content)  # Execute the script content
    except OSError as e:
        print("Unable to open file", file)

#### Web functions ####
def webpage():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pico W Payload Selector</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            button { font-size: 20px; padding: 10px 20px; margin: 10px; }
        </style>
    </head>
    <body>
        <h1>Pico W Payload Selector</h1>
        <form action="/execute" method="post">
            <button type="submit" name="payload" value="payload1">Execute Payload 1</button>
        </form>
        <form action="/execute" method="post">
            <button type="submit" name="payload" value="payload2">Execute Payload 2</button>
        </form>
    </body>
    </html>
    """

def base(request: Request):
    return Response(request, webpage(), content_type='text/html')

def execute_payload(request: Request):
    payload = request.form_data.get("payload")
    if payload == "payload1":
        runScript("payload1.py")
    elif payload == "payload2":
        runScript("payload2.py")
    else:
        return Response(request, "Invalid payload selected.", content_type='text/html')

    # Execute the selected payload script
    try:
        result_message = f"Executed {payload}.py successfully."
    except Exception as e:
        result_message = f"Error executing {payload}.py: {str(e)}"

    return Response(request, f"{webpage()}<p>{result_message}</p>", content_type='text/html')

#### Server start ####
def server_start():
    # WiFi credentials
    WIFI_SSID = secrets.SSID
    WIFI_PASSWORD = secrets.PASSWORD

    print("Connecting to WiFi")

    # Set static IP address
    ipv4 = ipaddress.IPv4Address("192.168.100.42")
    netmask = ipaddress.IPv4Address("255.255.255.0")
    gateway = ipaddress.IPv4Address("192.168.100.1")
    wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)
    # Connect to your SSID
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)

    # Define routes
    @server.route("/")
    def base(request: Request):
        return Response(request, webpage(), content_type='text/html')

    @server.route("/execute", methods=[POST])
    def execute_payload(request: Request):
        payload = request.form_data.get("payload")
        if payload == "payload1":
            runScript("payload1.py")
        elif payload == "payload2":
            runScript("payload2.py")
        else:
            return Response(request, "Invalid payload selected.", content_type='text/html')

        # Execute the selected payload script
        try:
            result_message = f"Executed {payload}.py successfully."
        except Exception as e:
            result_message = f"Error executing {payload}.py: {str(e)}"

        return Response(request, f"{webpage()}<p>{result_message}</p>", content_type='text/html')

    # Start the server
    print(f"Starting server at http://{wifi.radio.ipv4_address}")
    server.serve_forever(str(wifi.radio.ipv4_address))

# Check programming status and start server
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if not progStatus:
    print("Starting runtime sequence")
    server_start()
else:
    print("Update your payload")

