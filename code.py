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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico W Payload Selector</title>
    <style>
        /* Dark, sleek background with a subtle gradient */
        body {
            font-family: 'Courier New', Courier, monospace;
            background: linear-gradient(135deg, #1b1b1b, #2c2c2c);
            color: #00ff00;
            text-align: center;
            padding: 50px;
            margin: 0;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }

        /* Form container with space between buttons */
        .form-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 30px;
        }

        form {
            margin: 0;
        }

        /* Button styling: professional, sleek, and modern */
        button {
            background-color: #000;
            color: #00ff00;
            border: 2px solid #00ff00;
            border-radius: 5px;
            font-size: 1.2rem;
            padding: 15px 30px;
            margin: 10px;
            cursor: pointer;
            text-transform: uppercase;
            font-weight: bold;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            background-color: #00ff00;
            color: #000;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
            border-color: #00ff00;
        }

        /* Responsive adjustments */
        @media (max-width: 600px) {
            h1 {
                font-size: 2rem;
            }

            button {
                font-size: 1rem;
                padding: 10px 20px;
            }

            .form-container {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <h1>Pico W Payload Selector</h1>
    <div class="form-container">
        <form action="/execute" method="post">
            <button type="submit" name="payload" value="payload1">Execute Payload 1</button>
        </form>
        <form action="/execute" method="post">
            <button type="submit" name="payload" value="payload2">Execute Payload 2</button>
        </form>
        <form action="/execute" method="post">
            <button type="submit" name="payload" value="payload">Execute WinPeas</button>
        </form>
    </div>
</body>
</html>

    """
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
        if payload == "payload":
            runScript("payload.py")
        elif payload == "payload1":
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

