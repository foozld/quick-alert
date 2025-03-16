// Configuration
const CONFIG = {
    BACKEND_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000/ws',
    REFRESH_INTERVAL: 300000, // 5 minutes
    MAP_CENTER: [39.8283, -98.5795], // Center of USA
    MAP_ZOOM: 4,
    MAX_ALERTS: 100
};

// Initialize map with custom settings
const map = L.map('map').setView(CONFIG.MAP_CENTER, CONFIG.MAP_ZOOM);

// Add OpenStreetMap tiles with earth tone style
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    className: 'map-tiles'
}).addTo(map);

// Initialize marker cluster group
const markers = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50,
    iconCreateFunction: function(cluster) {
        const count = cluster.getChildCount();
        let size = 'small';
        
        if (count > 50) size = 'large';
        else if (count > 10) size = 'medium';
        
        return L.divIcon({
            html: `<div class="cluster-icon cluster-${size}">${count}</div>`,
            className: 'custom-cluster',
            iconSize: L.point(40, 40)
        });
    }
});

map.addLayer(markers);

// Store alerts and WebSocket connection
let activeAlerts = new Map();
let ws;
let wsReconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// DOM elements
const alertsList = document.getElementById('alertsList');
const sourceFilter = document.getElementById('sourceFilter');

// Initialize WebSocket connection
function initializeWebSocket() {
    ws = new WebSocket(CONFIG.WS_URL);

    ws.onopen = () => {
        console.log('Connected to WebSocket');
        wsReconnectAttempts = 0;
        showConnectionStatus('Connected to alert system', 'success');
        // Initial data load
        fetchAlerts();
    };

    ws.onmessage = (event) => {
        const alerts = JSON.parse(event.data);
        alerts.forEach(alert => addAlert(alert));
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        showConnectionStatus('Connection error - Retrying...', 'error');
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
        showConnectionStatus('Disconnected from alert system', 'error');
        
        // Attempt to reconnect
        if (wsReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            wsReconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect (${wsReconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
                initializeWebSocket();
            }, 5000); // Wait 5 seconds before reconnecting
        }
    };
}

// Show connection status to user
function showConnectionStatus(message, type) {
    const statusDiv = document.createElement('div');
    statusDiv.className = `connection-status ${type}`;
    statusDiv.textContent = message;
    
    // Remove any existing status messages
    const existingStatus = document.querySelector('.connection-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    document.body.insertBefore(statusDiv, document.body.firstChild);
    
    // Remove success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => statusDiv.remove(), 3000);
    }
}

// Fetch initial alerts
async function fetchAlerts() {
    try {
        showConnectionStatus('Fetching alerts...', 'info');
        const response = await fetch(`${CONFIG.BACKEND_URL}/api/alerts`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Clear existing alerts
        clearAlerts();
        
        // Add all alerts
        data.alerts.forEach(alert => addAlert(alert));
        
        showConnectionStatus('Alerts updated', 'success');
    } catch (error) {
        console.error('Error fetching alerts:', error);
        showConnectionStatus(`Error: ${error.message}`, 'error');
    }
}

// Clear all alerts
function clearAlerts() {
    alertsList.innerHTML = '';
    markers.clearLayers();
    activeAlerts.clear();
}

// Add a single alert to the UI
function addAlert(alert) {
    // Check source filter
    const currentFilter = sourceFilter.value;
    if (currentFilter !== 'all' && alert.source !== currentFilter) {
        return;
    }
    
    // Create alert card
    const alertCard = document.createElement('div');
    alertCard.className = `alert-card severity-${getSeverityClass(alert)}`;
    alertCard.setAttribute('data-alert-id', alert.id || Date.now());
    
    alertCard.innerHTML = `
        <div class="alert-source">${capitalizeFirst(alert.source)}</div>
        <div class="alert-text">${alert.text}</div>
        ${alert.location ? `<div class="alert-location">📍 ${alert.location}</div>` : ''}
        <div class="alert-time">${formatDate(alert.created_at)}</div>
    `;
    
    // Add click handler to center map on alert location
    if (alert.coordinates) {
        alertCard.addEventListener('click', () => {
            map.setView([alert.coordinates.lat, alert.coordinates.lon], 10);
        });
        alertCard.style.cursor = 'pointer';
    }
    
    // Add to list
    alertsList.insertBefore(alertCard, alertsList.firstChild);
    
    // Add marker if coordinates exist
    if (alert.coordinates) {
        addMarker(alert);
    }
    
    // Store alert
    activeAlerts.set(alert.id || Date.now(), alert);
    
    // Limit number of displayed alerts
    while (alertsList.children.length > CONFIG.MAX_ALERTS) {
        const oldestAlert = alertsList.lastChild;
        const oldestAlertId = oldestAlert.getAttribute('data-alert-id');
        activeAlerts.delete(oldestAlertId);
        alertsList.removeChild(oldestAlert);
    }
}

// Add marker to map
function addMarker(alert) {
    const marker = L.marker([alert.coordinates.lat, alert.coordinates.lon], {
        icon: createCustomIcon(alert.severity)
    }).bindPopup(createPopupContent(alert));
    
    markers.addLayer(marker);
}

// Create custom icon based on severity
function createCustomIcon(severity) {
    const iconColor = severity === 'Extreme' ? '#8B0000' :
                     severity === 'Severe' ? '#DAA520' :
                     '#4682B4';
    
    return L.divIcon({
        className: 'custom-marker',
        html: `<div class="marker-pin" style="background-color: ${iconColor}"></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    });
}

// Create popup content
function createPopupContent(alert) {
    return `
        <div class="popup-content">
            <strong>${capitalizeFirst(alert.source)}</strong>
            <p>${alert.text}</p>
            <small>${formatDate(alert.created_at)}</small>
        </div>
    `;
}

// Helper functions
function getSeverityClass(alert) {
    if (alert.severity === 'Extreme') return 'high';
    if (alert.severity === 'Severe') return 'medium';
    return 'low';
}

function capitalizeFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Event listeners
sourceFilter.addEventListener('change', () => {
    clearAlerts();
    activeAlerts.forEach(alert => addAlert(alert));
});

// Initialize WebSocket connection
initializeWebSocket();

// Refresh data periodically
setInterval(fetchAlerts, CONFIG.REFRESH_INTERVAL); 