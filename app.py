from gevent import monkey; monkey.patch_all()
from bottle import request, Bottle, template, abort, static_file
from time import sleep

app = Bottle()

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

# Route to index
@app.route('/index')
@app.route('/')
def index():
    client_ip = request.environ.get('REMOTE_ADDR')
    print(f"Client ip: {client_ip}")
    return template('index')

@app.route('/websocket')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    client_ip = request.environ.get('REMOTE_ADDR')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    ip_list.add(client_ip)
    ip_history.add(client_ip)
    print(f"{client_ip} has connected.")
    while True:
        try:
            message = wsock.receive()
            wsock.send("Your message was: %r" % message)
            print("message {}".format(message))
        except WebSocketError:
            break
    
    ip_list.remove(client_ip)
    print(f"{client_ip} has disconnected.")
    

@app.route('/stream')
def stream():
    yield 'START'
    sleep(2)
    yield 'MIDDLE'
    sleep(2)
    yield 'STOP'

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("0.0.0.0", 8080), app,
                    handler_class=WebSocketHandler)
server.serve_forever()

app.run(host='localhost', port=8080, debug=True)