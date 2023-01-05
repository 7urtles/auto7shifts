
import websocket
import json
from time import sleep
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzI4MDEwNTQuODcxOTk2LCJuYmYiOjE2NzI4MDEwNTQuODcxOTk2LCJleHAiOjE2NzI4MTU0NTQuODcxOTk2LCJpZGVudGl0eV9pZCI6MjQ1ODU1MCwidXNlcl9pZCI6NDg0OTQ1OSwiY29tcGFueV9pZCI6MTM5ODcxLCJpcF9hZGRyZXNzIjoiMjYwNTphNjAxOmFlZjk6MDozOWViOmM3MDI6NmFhNjo1NzgxIn0.AvWjoQZIibYhc3-uvbTOwZ_74KS_dYpWk_Tbb17xq-I"
socket_url = "wss://phx-ws.7shifts.com/auth_user_socket/websocket?token={token}&vsn=2.0.0"

message = json.dumps([None,"51","phoenix","heartbeat",{}])

ws = websocket.WebSocket()
ws.connect(socket_url, origin="https://app.7shifts.com")

while True:
    try:
        sent = ws.send(message)
        print(sent)
        result = ws.recv()
        print(result)
        sleep(5)
        
    except Exception as e:
        print(e)
        break
