// Initialize the room connection
function initRoom(roomId) {
	console.log("Initializing room with ID:", roomId);
	
	// Connect to WebSocket
	const socket = new WebSocket(
		'ws://' + window.location.host + '/ws/'
	);
	
	// Current user id
	let uid = "";

	socket.onopen = function(e) {
		console.log("WebSocket connection established");
		// Join the room
		socket.send(JSON.stringify({
			'join': roomId
		}));
	};
	
	socket.onclose = function(e) {
		console.log("WebSocket connection closed");
		// Don't redirect on close - just try to reconnect
		setTimeout(function() {
			console.log("Attempting to reconnect...");
			initRoom(roomId);
		}, 1000);
	};
	
	socket.onerror = function(e) {
		console.error("WebSocket error:", e);
	};

	window.onload = function() {
		wb = new Whiteboard("whiteboard", onDraw);
	};

	// Process websocket message
	socket.onmessage = function(event) {
		const data = JSON.parse(event.data);
		
		// Only redirect if explicitly told to exit
		if (data.exit === 1) { 
			console.log("Server requested exit");
			window.location.href = '/'; 
		}

		if (data.join) {
			uid = data.join;
			console.log("Joined as user " + uid);
		} else if (data.type == "txt_update") {
			document.getElementById("editor").value = data.data;
		} else if (data.type == "wb_buffer") {
			wb.setCanvasData(data.data);
		}

	};

	// Make onTextChange available globally
	window.onTextChange = function() {
		const content = document.getElementById("editor").value;
		socket.send(JSON.stringify({ id: uid, type: "txt_update", data: content }));
	};

	// Make onDraw available globally
	window.onDraw = function(buff, opt) {
		wb.draw(buff, opt);
		socket.send(JSON.stringify({ id: uid, type: "wb_buffer", data: wb.getCanvasData() }));
	};

	// Store socket in window object so it can be accessed globally
	window.roomSocket = socket;
}

// Session timer function
function startSessionTimer(seconds) {
	const timerElement = document.getElementById('timer');
	let timeLeft = seconds;
	
	// Update timer every second
	const timerInterval = setInterval(function() {
		timeLeft--;
		
		// Format time as MM:SS
		const minutes = Math.floor(timeLeft / 60);
		const secs = timeLeft % 60;
		timerElement.textContent = `Time remaining: ${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
		
		// Change color when less than 5 minutes
		if (timeLeft < 300) {
			timerElement.className = 'alert alert-warning';
		}
		
		// Change color when less than 1 minute
		if (timeLeft < 60) {
			timerElement.className = 'alert alert-danger';
		}
		
		// End session when timer reaches 0
		if (timeLeft <= 0) {
			clearInterval(timerInterval);
			
			// Remove the navigation warning
			window.onbeforeunload = null;
			
			// Show alert and redirect
			alert('Your interview session has ended. Thank you for participating!');
			window.location.href = '/';
		}
	}, 1000);
	
	// Store timer in window object so it can be accessed globally
	window.sessionTimer = timerInterval;
}

// Make sure this function is called when the page loads
document.addEventListener('DOMContentLoaded', function() {
	const roomIdElement = document.getElementById('roomId');
	if (roomIdElement) {
		const roomId = roomIdElement.value;
		if (roomId) {
			initRoom(roomId);
		} else {
			console.error("Room ID is empty");
		}
	} else {
		console.error("Room ID element not found");
	}
});