const socket = new WebSocket("ws://localhost:8000/ws/");

window.onload = function () {
	wb = new Whiteboard("whiteboard", onDraw);
};

socket.onmessage = function(event) {
	const data = JSON.parse(event.data);
	
	if (data.type == "txt_update") {
		document.getElementById("editor").value = data.data;
	} else if (data.type == "wb_buffer") {
		wb.setCanvasData(data.data);
	}

};

function onTextChange() {
	const content = document.getElementById("editor").value;
	socket.send(JSON.stringify({ room: "", type: "txt_update", data: content }));
}

function onDraw(buff, opt) {
	wb.draw(buff, opt);

	socket.send(JSON.stringify({ type: "wb_buffer", data: wb.getCanvasData() }));
}