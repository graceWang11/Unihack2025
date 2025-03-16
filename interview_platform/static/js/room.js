// Global whiteboard variable
let wb;

// Initialize the room connection
function initRoom(roomId) {
	console.log("Initializing room with ID:", roomId);
	
	// Connect to WebSocket - handle both HTTP and HTTPS
	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	const socket = new WebSocket(
		`${protocol}//${window.location.host}/ws/`
	);
	
	// Current user id
	let uid = "";
	let timerInterval = null;
	let sessionEndTime = null;

	socket.onopen = function(e) {
		console.log("WebSocket connection established");
		// Join the room
		socket.send(JSON.stringify({
			'join': roomId
		}));
		
		// Request timer state
		socket.send(JSON.stringify({
			'type': 'get_timer'
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

	// Initialize whiteboard when the window loads
	if (!wb && document.getElementById("whiteboard")) {
		wb = new Whiteboard("whiteboard", onDraw);
	}

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
			if (wb) {
				wb.setCanvasData(data.data);
			}
		} else if (data.type == "timer_update") {
			// Update the timer with the server's time
			updateTimerFromServer(data.end_time);
		}
	};

	// Make onTextChange available globally
	window.onTextChange = function() {
		const content = document.getElementById("editor").value;
		socket.send(JSON.stringify({ id: uid, type: "txt_update", data: content }));
	};

	// Make onDraw available globally
	window.onDraw = function(buff, opt) {
		if (wb) {
			wb.draw(buff, opt);
			socket.send(JSON.stringify({ id: uid, type: "wb_buffer", data: wb.getCanvasData() }));
		}
	};

	// Store socket in window object so it can be accessed globally
	window.roomSocket = socket;
	
	// Function to update timer from server time
	function updateTimerFromServer(endTimeStr) {
		try {
			// Parse the end time from the server
			sessionEndTime = new Date(endTimeStr);
			console.log("Session will end at:", sessionEndTime, "Current time:", Date.now());
			
			// Clear any existing timer
			if (timerInterval) {
				clearInterval(timerInterval);
			}
			
			// Start a new timer based on the server end time
			updateTimerDisplay();
			timerInterval = setInterval(updateTimerDisplay, 1000);
		} catch (error) {
			console.error("Error updating timer:", error);
		}
	}
	
	// Function to update the timer display
	function updateTimerDisplay() {
		try {
			const timerElement = document.getElementById('timer');
			if (!timerElement || !sessionEndTime) {
				console.error("Timer element or sessionEndTime not found");
				return;
			}
			
			const now = Date.now();
			const timeLeft = Math.max(0, Math.floor((sessionEndTime - now) / 1000));
			
			// Log without trying to call toISOString on a number
			console.log("Time left:", timeLeft, "seconds", "Current time:", new Date(now).toISOString());
			
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
				
				// Mark the session as expired on the server
				socket.send(JSON.stringify({
					'type': 'expire_session',
					'room': roomId
				}));
				
				// Show alert and redirect
				alert('Your interview session has ended. Thank you for participating!');
				window.location.href = '/?refresh=1';
			}
		} catch (error) {
			console.error("Error updating timer display:", error);
		}
	}
}

// Session timer function - now just sends a request to start the timer on the server
function startSessionTimer(seconds) {
	console.log("Starting session timer for", seconds, "seconds");
	const roomId = document.getElementById('roomId').value;
	
	if (!roomId) {
		console.error("Cannot start timer: roomId not available");
		return;
	}
	
	if (!window.roomSocket) {
		console.error("Cannot start timer: roomSocket not available");
		return;
	}
	
	if (window.roomSocket.readyState !== WebSocket.OPEN) {
		console.error("Cannot start timer: WebSocket not open");
		return;
	}
	
	console.log("Sending start_timer request to server for room", roomId);
	// Send request to start timer on the server
	try {
		window.roomSocket.send(JSON.stringify({
			'type': 'start_timer',
			'room': roomId,
			'duration': seconds
		}));
	} catch (error) {
		console.error("Error sending start_timer request:", error);
	}
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

// Make the clearWhiteboard function globally available
window.clearWhiteboard = function() {
	console.log("Clearing whiteboard...");
	if (!wb) {
		console.error("Whiteboard not initialized");
		return;
	}
	
	const canvas = document.getElementById("whiteboard");
	if (!canvas) {
		console.error("Whiteboard canvas not found");
		return;
	}
	
	const ctx = canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	
	// Send the cleared whiteboard to other users
	if (window.onDraw) {
		window.onDraw(wb.getCanvasData(), {clear: true});
	}
};

// Also make the other whiteboard functions globally available
window.setWBColor = function() {
	if (wb) {
		wb.strokeStyle = document.getElementById("colorPicker").value;
	} else {
		console.error("Whiteboard not initialized");
	}
};

window.setWBLine = function() {
	if (wb) {
		wb.lineWidth = document.getElementById("lineWidth").value;
	} else {
		console.error("Whiteboard not initialized");
	}
};