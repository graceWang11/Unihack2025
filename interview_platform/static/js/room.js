// room.js - Version 2.0.0 (Forced update)
console.log("Loading room.js version 2.0.0");

// Global variables
let wb = null;
let socket = null;
let uid = "";
let timerInterval = null;
let sessionEndTime = null;
let whiteBoardInitialized = false;

// Initialize the room connection
function initRoom(roomId) {
	console.log("Initializing room with ID:", roomId);
	
	// Connect to WebSocket - handle both HTTP and HTTPS
	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	socket = new WebSocket(
		`${protocol}//${window.location.host}/ws/`
	);
	
	// Make socket globally available
	window.roomSocket = socket;
	
	socket.onopen = function(e) {
		console.log("WebSocket connection established");
		// Join the room
		socket.send(JSON.stringify({
			'join': roomId
		}));
		
		// Initialize whiteboard immediately after socket is connected
		initWhiteboard();
		
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

	// Process websocket message
	socket.onmessage = function(event) {
		try {
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
				if (window.wb) {
					window.wb.setCanvasData(data.data);
				}
			} else if (data.type == "timer_update") {
				// Update the timer with the server's time
				updateTimerFromServer(data.end_time);
			}
		} catch (error) {
			console.error("Error processing WebSocket message:", error);
		}
	};

	// Make onTextChange available globally
	window.onTextChange = function() {
		if (!socket || socket.readyState !== WebSocket.OPEN) {
			console.error("Cannot send text update: WebSocket not open");
			return;
		}
		
		const content = document.getElementById("editor").value;
		socket.send(JSON.stringify({ id: uid, type: "txt_update", data: content }));
	};
}

// Initialize the whiteboard
function initWhiteboard() {
	console.log("Initializing whiteboard (version 2.0)");
	const canvas = document.getElementById("whiteboard");
	if (!canvas) {
		console.error("Whiteboard canvas not found");
		return;
	}
	
	try {
		// Create the whiteboard object with delayed verification
		window.wb = new Whiteboard("whiteboard", function(buff, opt) {
			// This is the onDraw callback
			if (window.wb) {
				window.wb.draw(buff, opt);
				if (socket && socket.readyState === WebSocket.OPEN) {
					socket.send(JSON.stringify({ 
						id: uid, 
						type: "wb_buffer", 
						data: window.wb.getCanvasData() 
					}));
				}
			}
		});
		
		// Make wb globally available and mark as initialized
		wb = window.wb;
		whiteBoardInitialized = true;
		
		// Also set onDraw globally
		window.onDraw = function(buff, opt) {
			if (window.wb) {
				window.wb.draw(buff, opt);
				if (socket && socket.readyState === WebSocket.OPEN) {
					socket.send(JSON.stringify({ 
						id: uid, 
						type: "wb_buffer", 
						data: window.wb.getCanvasData() 
					}));
				}
			}
		};
		
		console.log("Whiteboard initialized successfully");
		
		// Initialize the whiteboard controls
		initWhiteboardControls();
	} catch (error) {
		console.error("Error initializing whiteboard:", error);
	}
}

// Initialize whiteboard controls directly
function initWhiteboardControls() {
	console.log("Setting up whiteboard controls");
	
	// Define clearWhiteboard function globally
	window.clearWhiteboard = function() {
		console.log("Clearing whiteboard (v2)");
		if (!window.wb) {
			console.error("Cannot clear: Whiteboard not initialized");
			return;
		}
		
		try {
			const canvas = document.getElementById("whiteboard");
			if (!canvas) {
				console.error("Whiteboard canvas not found");
				return;
			}
			
			const ctx = canvas.getContext("2d");
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			console.log("Canvas cleared successfully");
			
			// Send the cleared whiteboard to other users
			if (socket && socket.readyState === WebSocket.OPEN) {
				socket.send(JSON.stringify({ 
					id: uid, 
					type: "wb_buffer", 
					data: window.wb.getCanvasData() 
				}));
				console.log("Clear event sent to server");
			}
		} catch (error) {
			console.error("Error clearing whiteboard:", error);
		}
	};
	
	// Define setWBColor function globally
	window.setWBColor = function() {
		console.log("Setting whiteboard color (v2)");
		if (!window.wb) {
			console.error("Cannot set color: Whiteboard not initialized");
			return;
		}
		
		try {
			const colorPicker = document.getElementById("colorPicker");
			if (!colorPicker) {
				console.error("Color picker not found");
				return;
			}
			
			window.wb.strokeStyle = colorPicker.value;
			console.log("Color set to:", colorPicker.value);
		} catch (error) {
			console.error("Error setting whiteboard color:", error);
		}
	};
	
	// Define setWBLine function globally
	window.setWBLine = function() {
		console.log("Setting whiteboard line width (v2)");
		if (!window.wb) {
			console.error("Cannot set line width: Whiteboard not initialized");
			return;
		}
		
		try {
			const lineWidth = document.getElementById("lineWidth");
			if (!lineWidth) {
				console.error("Line width control not found");
				return;
			}
			
			window.wb.lineWidth = lineWidth.value;
			console.log("Line width set to:", lineWidth.value);
		} catch (error) {
			console.error("Error setting whiteboard line width:", error);
		}
	};
}

// Function to update timer from server time
function updateTimerFromServer(endTimeStr) {
	try {
		// Parse the end time from the server - carefully
		console.log("Raw end time from server:", endTimeStr);
		const endTime = new Date(endTimeStr);
		console.log("Parsed end time:", endTime);
		
		sessionEndTime = endTime;
		
		// Clear any existing timer
		if (timerInterval) {
			clearInterval(timerInterval);
		}
		
		// Start a new timer based on the server end time
		updateTimerDisplay();
		timerInterval = setInterval(updateTimerDisplay, 1000);
		
		console.log("Timer started successfully");
	} catch (error) {
		console.error("Error updating timer:", error);
	}
}

// Function to update the timer display
function updateTimerDisplay() {
	try {
		const timerElement = document.getElementById('timer');
		if (!timerElement) {
			console.error("Timer element not found");
			return;
		}
		
		if (!sessionEndTime) {
			console.error("Session end time not set");
			return;
		}
		
		// Calculate time left in milliseconds
		const now = new Date();
		const timeLeftMs = sessionEndTime.getTime() - now.getTime();
		const timeLeft = Math.max(0, Math.floor(timeLeftMs / 1000));
		
		console.log("Time remaining:", timeLeft, "seconds");
		
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
			if (socket && socket.readyState === WebSocket.OPEN) {
				socket.send(JSON.stringify({
					'type': 'expire_session',
					'room': document.getElementById('roomId').value
				}));
			}
			
			// Show alert and redirect
			alert('Your interview session has ended. Thank you for participating!');
			window.location.href = '/?refresh=1';
		}
	} catch (error) {
		console.error("Error updating timer display:", error);
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
	
	if (!socket || socket.readyState !== WebSocket.OPEN) {
		console.error("Cannot start timer: WebSocket not open");
		return;
	}
	
	console.log("Sending start_timer request to server for room", roomId);
	// Send request to start timer on the server
	try {
		socket.send(JSON.stringify({
			'type': 'start_timer',
			'room': roomId,
			'duration': seconds
		}));
	} catch (error) {
		console.error("Error sending start_timer request:", error);
	}
}

// Make startSessionTimer available globally
window.startSessionTimer = startSessionTimer;

// Initialize the room when the page loads
document.addEventListener('DOMContentLoaded', function() {
	console.log("DOM loaded, initializing room (v2.0)");
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