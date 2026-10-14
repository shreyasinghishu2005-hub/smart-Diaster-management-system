/**
 * Leaflet.js Emergency Response Map Manager
 * Supports:
 * - Dynamic Light/Dark tile layer switching
 * - Incident rendering with priority color-coded markers
 * - Nearby emergency facility overlays (Hospitals, Fire, Police, Shelters)
 * - Interactive report location picker with reverse geocoding & manual fallback
 */

const EmergencyMapManager = (function () {
    "use strict";

    // Tile Layer Definitions
    const LIGHT_TILES = {
        url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        fallbackUrl: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: 19,
    };

    const DARK_TILES = {
        url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        fallbackUrl: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: 19,
    };

    // Helper: Determine current active theme
    function getCurrentTheme() {
        return document.documentElement.getAttribute("data-theme") || "light";
    }

    // Helper: Create theme tile layer
    function createTileLayer(theme) {
        const config = theme === "dark" ? DARK_TILES : LIGHT_TILES;
        return L.tileLayer(config.url, {
            attribution: config.attribution,
            maxZoom: config.maxZoom,
            subdomains: "abcd",
        });
    }

    // Custom Marker Icons
    function getIncidentIcon(priority, type) {
        const colors = {
            Critical: "#DC2626",
            High: "#EA580C",
            Medium: "#D97706",
            Low: "#16A34A",
        };
        const color = colors[priority] || "#2563EB";

        const iconSymbols = {
            Flood: "🌊",
            Fire: "🔥",
            Earthquake: "🌋",
            "Road Accident": "🚗",
            "Medical Emergency": "🏥",
            Other: "⚠️",
        };
        const symbol = iconSymbols[type] || "🚨";

        return L.divIcon({
            className: "custom-div-icon",
            html: `<div style="
                background-color: ${color};
                width: 32px;
                height: 32px;
                border-radius: 50% 50% 50% 0;
                transform: rotate(-45deg);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                border: 2px solid #FFFFFF;
            ">
                <span style="transform: rotate(45deg); font-size: 14px; line-height: 1;">${symbol}</span>
            </div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
        });
    }

    function getResourceIcon(resourceType) {
        const configs = {
            Hospital: { bg: "#2563EB", icon: "🏥" },
            "Fire Station": { bg: "#DC2626", icon: "🚒" },
            "Police Station": { bg: "#1E293B", icon: "🚓" },
            "Relief Shelter": { bg: "#059669", icon: "⛺" },
        };
        const config = configs[resourceType] || { bg: "#4B5563", icon: "📍" };

        return L.divIcon({
            className: "custom-resource-icon",
            html: `<div style="
                background-color: ${config.bg};
                width: 28px;
                height: 28px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.25);
                border: 2px solid #FFFFFF;
                font-size: 13px;
            ">${config.icon}</div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14],
            popupAnchor: [0, -14],
        });
    }

    // -------------------------------------------------------------
    // 1. Fullscreen Main Interactive Map
    // -------------------------------------------------------------
    function initFullscreenMap(containerId) {
        const mapContainer = document.getElementById(containerId);
        if (!mapContainer) return;

        // Default center (San Francisco demo region)
        const map = L.map(containerId).setView([37.7749, -122.4194], 13);

        let currentTileLayer = createTileLayer(getCurrentTheme()).addTo(map);

        // Switch tiles when theme changes
        window.addEventListener("themeChanged", function (e) {
            map.removeLayer(currentTileLayer);
            currentTileLayer = createTileLayer(e.detail.theme).addTo(map);
        });

        const incidentLayer = L.layerGroup().addTo(map);
        const resourceLayer = L.layerGroup().addTo(map);

        function loadMapData() {
            const filterType = document.getElementById("filterDisasterType")?.value || "All";
            const filterPriority = document.getElementById("filterPriority")?.value || "All";
            const filterStatus = document.getElementById("filterStatus")?.value || "All";
            const showResources = document.getElementById("toggleResources")?.checked ?? true;

            // Load incidents
            fetch(`/api/incidents?type=${filterType}&priority=${filterPriority}&status=${filterStatus}`)
                .then((res) => res.json())
                .then((data) => {
                    incidentLayer.clearLayers();
                    const features = data.features || [];

                    features.forEach((feat) => {
                        const coords = feat.geometry.coordinates;
                        const props = feat.properties;
                        const marker = L.marker([coords[1], coords[0]], {
                            icon: getIncidentIcon(props.priority, props.disaster_type),
                        });

                        const popupHtml = `
                            <div style="min-width: 220px;">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span class="badge badge-priority badge-priority-${props.priority.toLowerCase()}">${props.priority}</span>
                                    <span class="badge badge-status badge-status-${props.status.toLowerCase().replace(/ /g, '-')}">${props.status}</span>
                                </div>
                                <h6 class="fw-bold mb-1 mt-1 text-truncate">${props.title}</h6>
                                <p class="small text-muted mb-1"><i class="bi bi-geo-alt"></i> ${props.location_name}</p>
                                <p class="small text-muted mb-2"><i class="bi bi-clock"></i> ${props.datetime}</p>
                                <a href="/incident/${props.id}" class="btn btn-sm btn-primary-custom w-100 text-center">View Incident Details</a>
                            </div>
                        `;
                        marker.bindPopup(popupHtml);
                        incidentLayer.addLayer(marker);
                    });

                    // Update UI counter if exists
                    const countElem = document.getElementById("mapIncidentCount");
                    if (countElem) {
                        countElem.innerText = `${features.length} Incidents Displayed`;
                    }
                })
                .catch((err) => console.error("Error loading incidents:", err));

            // Load resources
            if (showResources) {
                fetch("/api/resources")
                    .then((res) => res.json())
                    .then((data) => {
                        resourceLayer.clearLayers();
                        (data.features || []).forEach((feat) => {
                            const coords = feat.geometry.coordinates;
                            const props = feat.properties;
                            const marker = L.marker([coords[1], coords[0]], {
                                icon: getResourceIcon(props.resource_type),
                            });

                            const popupHtml = `
                                <div style="min-width: 200px;">
                                    <span class="badge bg-secondary mb-1">${props.resource_type}</span>
                                    <h6 class="fw-bold mb-1">${props.name}</h6>
                                    <p class="small text-muted mb-1">${props.address}</p>
                                    <p class="small text-muted mb-1"><strong>Phone:</strong> ${props.phone}</p>
                                    <p class="small text-muted mb-0"><strong>Capacity:</strong> ${props.capacity}</p>
                                </div>
                            `;
                            marker.bindPopup(popupHtml);
                            resourceLayer.addLayer(marker);
                        });
                    })
                    .catch((err) => console.error("Error loading resources:", err));
            } else {
                resourceLayer.clearLayers();
            }
        }

        // Attach filter listeners
        ["filterDisasterType", "filterPriority", "filterStatus", "toggleResources"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener("change", loadMapData);
            }
        });

        loadMapData();
        return map;
    }

    // -------------------------------------------------------------
    // 2. Incident Reporting Location Picker
    // -------------------------------------------------------------
    function initReportLocationPicker(containerId) {
        const mapContainer = document.getElementById(containerId);
        if (!mapContainer) return;

        const defaultLat = 37.7749;
        const defaultLng = -122.4194;

        const latInput = document.getElementById("latitude");
        const lngInput = document.getElementById("longitude");
        const locNameInput = document.getElementById("location_name");

        const initialLat = latInput && latInput.value ? parseFloat(latInput.value) : defaultLat;
        const initialLng = lngInput && lngInput.value ? parseFloat(lngInput.value) : defaultLng;

        const map = L.map(containerId).setView([initialLat, initialLng], 13);
        let currentTileLayer = createTileLayer(getCurrentTheme()).addTo(map);

        window.addEventListener("themeChanged", function (e) {
            map.removeLayer(currentTileLayer);
            currentTileLayer = createTileLayer(e.detail.theme).addTo(map);
        });

        let marker = L.marker([initialLat, initialLng], {
            draggable: true,
            icon: L.divIcon({
                className: "picker-icon",
                html: `<div style="
                    background-color: #DC2626;
                    width: 32px;
                    height: 32px;
                    border-radius: 50% 50% 50% 0;
                    transform: rotate(-45deg);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.35);
                    border: 2px solid #FFFFFF;
                "><span style="transform: rotate(45deg); color: #fff; font-size: 14px;">📍</span></div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 32],
            }),
        }).addTo(map);

        function updateLocationFields(lat, lng) {
            if (latInput) latInput.value = lat.toFixed(6);
            if (lngInput) lngInput.value = lng.toFixed(6);

            // Attempt reverse geocoding via Nominatim
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                .then((res) => res.json())
                .then((data) => {
                    if (data && data.display_name && locNameInput && !locNameInput.value.trim()) {
                        locNameInput.value = data.display_name.split(",").slice(0, 3).join(", ");
                    }
                })
                .catch(() => {
                    // Fallback gracefully without throwing
                });
        }

        // Click map to reposition marker
        map.on("click", function (e) {
            marker.setLatLng(e.latlng);
            updateLocationFields(e.latlng.lat, e.latlng.lng);
        });

        // Drag marker to reposition
        marker.on("dragend", function (e) {
            const pos = marker.getLatLng();
            updateLocationFields(pos.lat, pos.lng);
        });

        // Manual coordinate input event listeners
        if (latInput && lngInput) {
            const onManualCoordChange = function () {
                const manualLat = parseFloat(latInput.value);
                const manualLng = parseFloat(lngInput.value);
                if (!isNaN(manualLat) && !isNaN(manualLng)) {
                    if (manualLat >= -90 && manualLat <= 90 && manualLng >= -180 && manualLng <= 180) {
                        const newLatLng = L.latLng(manualLat, manualLng);
                        marker.setLatLng(newLatLng);
                        map.panTo(newLatLng);
                    }
                }
            };
            latInput.addEventListener("change", onManualCoordChange);
            lngInput.addEventListener("change", onManualCoordChange);
        }

        // HTML5 Geolocation Button with explicit user consent & permission handling
        const geoBtn = document.getElementById("btnUseCurrentLocation");
        if (geoBtn) {
            geoBtn.addEventListener("click", function () {
                if (!navigator.geolocation) {
                    alert("Geolocation is not supported by your browser. Please enter coordinates manually.");
                    return;
                }

                geoBtn.disabled = true;
                geoBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Acquiring GPS...';

                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const userLat = position.coords.latitude;
                        const userLng = position.coords.longitude;
                        marker.setLatLng([userLat, userLng]);
                        map.setView([userLat, userLng], 15);
                        updateLocationFields(userLat, userLng);

                        geoBtn.disabled = false;
                        geoBtn.innerHTML = '<i class="bi bi-geo-alt-fill me-1"></i> Use My GPS Location';
                    },
                    function (error) {
                        geoBtn.disabled = false;
                        geoBtn.innerHTML = '<i class="bi bi-geo-alt-fill me-1"></i> Use My GPS Location';
                        let msg = "Unable to retrieve location.";
                        if (error.code === error.PERMISSION_DENIED) {
                            msg = "Location access was denied. You can select your location on the map or type coordinates manually.";
                        } else if (error.code === error.POSITION_UNAVAILABLE) {
                            msg = "Location information is unavailable.";
                        } else if (error.code === error.TIMEOUT) {
                            msg = "Location request timed out.";
                        }
                        alert(msg);
                    },
                    { timeout: 8000, enableHighAccuracy: true }
                );
            });
        }

        // Initial populate if empty
        if (latInput && !latInput.value) {
            updateLocationFields(initialLat, initialLng);
        }

        return map;
    }

    // -------------------------------------------------------------
    // 3. Incident Detail Map (Centered with nearby facilities)
    // -------------------------------------------------------------
    function initDetailMap(containerId, lat, lng, title, priority, disasterType, nearbyResources) {
        const mapContainer = document.getElementById(containerId);
        if (!mapContainer) return;

        const map = L.map(containerId).setView([lat, lng], 14);
        let currentTileLayer = createTileLayer(getCurrentTheme()).addTo(map);

        window.addEventListener("themeChanged", function (e) {
            map.removeLayer(currentTileLayer);
            currentTileLayer = createTileLayer(e.detail.theme).addTo(map);
        });

        // Incident marker
        const incidentMarker = L.marker([lat, lng], {
            icon: getIncidentIcon(priority, disasterType),
        }).addTo(map);

        incidentMarker.bindPopup(`
            <div style="min-width: 180px;">
                <span class="badge badge-priority badge-priority-${priority.toLowerCase()} mb-1">${priority}</span>
                <h6 class="fw-bold mb-1">${title}</h6>
                <p class="small text-muted mb-0">Ground Zero (${lat.toFixed(4)}, ${lng.toFixed(4)})</p>
            </div>
        `).openPopup();

        // Nearby facilities markers
        if (Array.isArray(nearbyResources)) {
            nearbyResources.forEach((res) => {
                const resMarker = L.marker([res.latitude, res.longitude], {
                    icon: getResourceIcon(res.resource_type),
                }).addTo(map);

                resMarker.bindPopup(`
                    <div style="min-width: 180px;">
                        <span class="badge bg-secondary mb-1">${res.resource_type}</span>
                        <h6 class="fw-bold mb-1">${res.name}</h6>
                        <p class="small text-muted mb-1">${res.address}</p>
                        <p class="small mb-1"><strong>Proximity:</strong> ${res.distance_km} km away</p>
                        <p class="small text-muted mb-0"><strong>Phone:</strong> ${res.phone}</p>
                    </div>
                `);
            });
        }

        return map;
    }

    return {
        initFullscreenMap: initFullscreenMap,
        initReportLocationPicker: initReportLocationPicker,
        initDetailMap: initDetailMap,
    };
})();
