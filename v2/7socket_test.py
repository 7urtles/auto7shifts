
import websocket
import json
from time import sleep
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NzM1MzE2ODQuOTg0NzY5LCJuYmYiOjE2NzM1MzE2ODQuOTg0NzY5LCJleHAiOjE2NzM1NDYwODQuOTg0NzY5LCJpZGVudGl0eV9pZCI6MjQ1ODU1MCwidXNlcl9pZCI6NDg0OTQ1OSwiY29tcGFueV9pZCI6MTM5ODcxLCJpcF9hZGRyZXNzIjoiMTk0LjE1Ni4xMzYuMTA2In0.ADY86ibsiKTdIPVpRw8Fr-7Bjni4HY-PBqz-hh1SBko"
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