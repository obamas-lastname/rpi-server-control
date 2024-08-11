import time
import socketpool
import secrets
import wifi
import board
from digitalio import DigitalInOut, Direction
from adafruit_httpserver import Server, Request, Response, POST
import microcontroller
import os

# WiFi credentials
WIFI_SSID = secrets.SSID
WIFI_PASSWORD = secrets.PASSWORD

# Set up onboard LED
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False

# Connect to WiFi
print(f"Connecting to {WIFI_SSID}...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID}")

# Initialize socket pool and server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# Define HTML page with payload selection buttons
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

# Route to serve the HTML page
@server.route("/")
def base(request: Request):
    return Response(request, webpage(), content_type='text/html')

def runScript(file):
    try:
        with open(file, "r", encoding='utf-8') as f:
            script_content = f.read()
        exec(script_content)  # Execute the script content
    except OSError as e:
        print("Unable to open file ", file)
# Route to handle payload execution
@server.route("/execute", methods=[POST])
def execute_payload(request: Request):
    payload = request.form_data.get("payload")
    if payload == "payload1":
        runScript("payload1.py")
    elif payload == "payload2":
        runScript("payload2.py")
    else:
        return Response(request, "Invalid payload selected.", content_type='text/html')

    # Check if the script exists
    if not os.path.exists(script_path):
        return Response(request, "Payload file not found.", content_type='text/html')

    # Execute the selected payload script
    try:
        result_message = f"Executed {payload}.py successfully."
    except Exception as e:
        result_message = f"Error executing {payload}.py: {str(e)}"

    return Response(request, f"{webpage()}<p>{result_message}</p>", content_type='text/html')

# Start the server
print(f"Starting server at http://{wifi.radio.ipv4_address}")
server.serve_forever(str(wifi.radio.ipv4_address))

