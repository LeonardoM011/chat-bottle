var ws = new WebSocket("ws://192.168.1.6:8080/websocket");
ws.onopen = function() {
    ws.send("Leonardo");
};

ws.onmessage = function (evt) {
    alert(evt.data);
};