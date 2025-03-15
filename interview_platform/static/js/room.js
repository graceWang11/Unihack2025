const socket = new WebSocket("ws://localhost:8000/ws/");

// Current user id
let uid = "";

window.onload = function() {
	wb = new Whiteboard("whiteboard", onDraw);
};

socket.onopen = function() {
	socket.send(JSON.stringify({join: roomId}));
}

// Process websocket message
socket.onmessage = function(event) {
	const data = JSON.parse(event.data);
	
	if (data.exit) { window.location.href = '/'; }

	if (data.join) {
		uid = data.join;
		console.log("Joined as user " + uid);
	} else if (data.type == "txt_update") {
		document.getElementById("editor").value = data.data;
	} else if (data.type == "wb_buffer") {
		wb.setCanvasData(data.data);
	}

};

function onTextChange() {
	const content = document.getElementById("editor").value;
	socket.send(JSON.stringify({ id: uid, type: "txt_update", data: content }));
}

function onDraw(buff, opt) {
	wb.draw(buff, opt);

	socket.send(JSON.stringify({ id: uid, type: "wb_buffer", data: wb.getCanvasData() }));
}