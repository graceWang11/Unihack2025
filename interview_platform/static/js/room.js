// room.js - Version 3.0.0 (Final Fix)
console.log("Loading room.js version 3.0.0");

// Global variables - explicitly attach to window
window.socket = null;
window.uid = "";
window.wb = null;
window.timerInterval = null;
window.sessionEndTime = null;
window.serverTimestamp = null;
window.sessionEndTimestamp = null;

// Initialize the room connection
function initRoom(roomId) {
	console.log("Initializing room with ID:", roomId);
	
	// Connect to WebSocket - handle both HTTP and HTTPS
	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	window.socket = new WebSocket(
		`${protocol}//${window.location.host}/ws/`
	);
	
	// Make socket globally available
	window.roomSocket = window.socket;
	
	window.socket.onopen = function(e) {
		console.log("WebSocket connection established");
		// Join the room
		window.socket.send(JSON.stringify({
			'join': roomId
		}));
		
		// Initialize whiteboard immediately after socket is connected
		initWhiteboard();
		
		// Request timer state
		window.socket.send(JSON.stringify({
			'type': 'get_timer'
		}));
		
		// Set up the text change handler
		if (document.getElementById('editor')) {
			document.getElementById('editor').addEventListener('keyup', function() {
				onTextChange();
			});
		}
	};
	
	window.socket.onclose = function(e) {
		console.log("WebSocket connection closed");
		// Don't redirect on close - just try to reconnect
		setTimeout(function() {
			console.log("Attempting to reconnect...");
			initRoom(roomId);
		}, 1000);
	};
	
	window.socket.onerror = function(e) {
		console.error("WebSocket error:", e);
	};

	// Process websocket message
	window.socket.onmessage = function(event) {
		try {
			const data = JSON.parse(event.data);
			
			// Only redirect if explicitly told to exit
			if (data.exit === 1) { 
				console.log("Server requested exit");
				window.location.href = '/'; 
			}

			if (data.join) {
				window.uid = data.join;
				console.log("Joined as user " + window.uid);
			} else if (data.type == "txt_update") {
				if (document.getElementById("editor")) {
					document.getElementById("editor").value = data.data;
				}
			} else if (data.type == "wb_buffer") {
				if (window.wb) {
					window.wb.setCanvasData(data.data);
				}
			} else if (data.type == "timer_update") {
				// Update the timer with the server's time
				updateTimerFromServer(data.end_time);
			} else if (data.type === 'global_time') {
				handleGlobalTime(data.timestamp);
			}
		} catch (error) {
			console.error("Error processing WebSocket message:", error);
		}
	};
}

// Initialize the whiteboard
function initWhiteboard() {
	console.log("Initializing whiteboard (version 3.0)");
	const canvas = document.getElementById("whiteboard");
	if (!canvas) {
		console.error("Whiteboard canvas not found");
		return;
	}
	
	try {
		// Create the whiteboard object with inline callback
		window.wb = new Whiteboard("whiteboard", function(buff, opt) {
			// This is the onDraw callback
			if (window.wb) {
				window.wb.draw(buff, opt);
				if (window.socket && window.socket.readyState === WebSocket.OPEN) {
					window.socket.send(JSON.stringify({ 
						id: window.uid, 
						type: "wb_buffer", 
						data: window.wb.getCanvasData() 
					}));
				}
			}
		});
		
		console.log("Whiteboard initialized successfully");
	} catch (error) {
		console.error("Error initializing whiteboard:", error);
	}
}

// Function to handle text changes in the editor
function onTextChange() {
	const editor = document.getElementById("editor");
	if (!editor) {
		console.error("Editor element not found");
		return;
	}
	
	if (!window.socket || window.socket.readyState !== WebSocket.OPEN) {
		console.error("Cannot send text update: WebSocket not open");
		return;
	}
	
	try {
		window.socket.send(JSON.stringify({
			'type': 'txt_update',
			'data': editor.value
		}));
	} catch (error) {
		console.error("Error sending text update:", error);
	}
}

// Simplest possible timer implementation
window.remainingSeconds = 900; // 15 minutes

// Start the timer immediately when the page loads
window.onload = function() {
	// Start a simple countdown timer
	window.timerInterval = setInterval(function() {
		try {
			const timerElement = document.getElementById('timer');
			if (!timerElement) return;
			
			// Decrement time
			window.remainingSeconds--;
			
			// Handle timer expiration
			if (window.remainingSeconds <= 0) {
				clearInterval(window.timerInterval);
				alert('Time is up!');
				window.location.href = '/';
				return;
			}
			
			// Update display
			const minutes = Math.floor(window.remainingSeconds / 60);
			const seconds = window.remainingSeconds % 60;
			const formattedTime = 
				String(minutes).padStart(2, '0') + ':' + 
				String(seconds).padStart(2, '0');
			
			timerElement.textContent = 'Time remaining: ' + formattedTime;
			
			// Update colors
			if (window.remainingSeconds < 60) {
				timerElement.className = 'alert alert-danger';
			} else if (window.remainingSeconds < 300) {
				timerElement.className = 'alert alert-warning';
			}
		} catch (e) {
			console.error("Simple timer error:", e);
		}
	}, 1000);
};

// Start a simple 15-minute timer
function startSessionTimer(seconds) {
	console.log("Starting simple session timer for", seconds, "seconds");
	
	if (window.timerInterval) {
		clearInterval(window.timerInterval);
	}
	
	window.remainingSeconds = seconds || 900; // Default 15 minutes
	
	updateTimerDisplay();
	window.timerInterval = setInterval(updateTimerDisplay, 1000);
	
	console.log("Simple timer started successfully");
}

// Make startSessionTimer available globally
window.startSessionTimer = startSessionTimer;
window.onTextChange = onTextChange;
window.updateTimerDisplay = updateTimerDisplay;
window.updateTimerFromServer = updateTimerFromServer;

// Handler for global time events
function handleGlobalTime(timestamp) {
	window.serverTimestamp = timestamp;
	
	// If we have an end time, update the timer display
	if (window.sessionEndTimestamp) {
		updateTimerDisplay();
	}
}

// Initialize the room when the page loads
document.addEventListener('DOMContentLoaded', function() {
	console.log("DOM loaded, initializing room (v3.0)");
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

function setWBColor() {
	wb.options.strokeStyle = document.getElementById('colorPicker').value;
}

function setWBLine() {
	wb.options.lineWidth = document.getElementById('lineWidth').value;
}