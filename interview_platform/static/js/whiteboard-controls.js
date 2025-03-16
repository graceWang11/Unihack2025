// Global whiteboard variable that will be initialized by room.js
let wb;

// Define whiteboard control functions in the global scope
function setWBColor() {
    console.log("Setting whiteboard color");
    const colorPicker = document.getElementById("colorPicker");
    if (!colorPicker) {
        console.error("Color picker not found");
        return;
    }
    
    if (typeof window.wb !== 'undefined') {
        window.wb.strokeStyle = colorPicker.value;
        console.log("Color set to:", colorPicker.value);
    } else {
        console.error("Whiteboard not initialized");
    }
}

function setWBLine() {
    console.log("Setting whiteboard line width");
    const lineWidth = document.getElementById("lineWidth");
    if (!lineWidth) {
        console.error("Line width control not found");
        return;
    }
    
    if (typeof window.wb !== 'undefined') {
        window.wb.lineWidth = lineWidth.value;
        console.log("Line width set to:", lineWidth.value);
    } else {
        console.error("Whiteboard not initialized");
    }
}

function clearWhiteboard() {
    console.log("Clearing whiteboard");
    const canvas = document.getElementById("whiteboard");
    if (!canvas) {
        console.error("Whiteboard canvas not found");
        return;
    }
    
    if (typeof window.wb === 'undefined') {
        console.error("Whiteboard not initialized");
        return;
    }
    
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    console.log("Canvas cleared");
    
    // Send the cleared whiteboard to other users
    if (typeof window.onDraw === 'function') {
        window.onDraw(window.wb.getCanvasData(), {clear: true});
        console.log("Clear event sent to other users");
    } else {
        console.error("onDraw function not available");
    }
}

// Check if whiteboard is initialized when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("Whiteboard controls loaded, checking for whiteboard initialization");
    setTimeout(function() {
        if (typeof window.wb === 'undefined') {
            console.warn("Whiteboard not initialized after page load");
        } else {
            console.log("Whiteboard is initialized and ready");
        }
    }, 2000);
}); 