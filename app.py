#!/usr/bin/python
from gevent import monkey; monkey.patch_all()
from bottle import request, Bottle, template, abort, static_file
from time import sleep
from fnwebsocket import *
import json

# We're using object oriented approach
app = Bottle()

# Sets for ip lists
ip_list = set()
ip_history = set()

# Route to javascript static files
@app.route('/static/scripts/<filename>')
def send_static(filename):
    return static_file(filename, root='./static/scripts')

# Route to css static files
@app.route('/static/styles/<filename>')
def send_static(filename):
    return static_file(filename, root='./static/styles')

@app.route('/static/favicon/<filename>')
def send_static(filename):
    return static_file(filename, root='./static/favicon')

# Route to index
@app.route('/index')
@app.route('/')
def index():
    client_ip = request.environ.get('REMOTE_ADDR')
    print(f"Client ip: {client_ip}")
    return template('index', client_ip=client_ip, users_online=len(ip_list))

# Websocket server clients connect to
@app.route('/websocket')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    client_ip = request.environ.get('REMOTE_ADDR')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    ip_list.add(client_ip)
    ip_history.add(client_ip)
    print(f"{client_ip} has connected.")
    #msg = { "ip_list": str(len(ip_list)) }
    #try:
        #wsock.send("Leon");
        #wsock.send(str(msg))
    #except WebSocketError:
    #    print("error")

    while True:
        try:
            message = wsock.receive()
            msg = {"message": f"Your message was: {message}"}
            wsock.send(json.dumps(msg))
            print(f"Message by {client_ip} is: {message}")
        except WebSocketError:
            print("error")
            break
    
    ip_list.remove(client_ip)
    print(f"{client_ip} has disconnected.")

# Starting web socket server
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("0.0.0.0", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()

# Finally starting our server
app.run(host='localhost', port=8080, debug=True)