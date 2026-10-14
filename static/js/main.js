/**
 * Smart Disaster Management & Emergency Response System
 * Client-Side Application Logic: Theme Switching, Client Validation, UI Helpers
 */

(function () {
    "use strict";

    // -------------------------------------------------------------
    // 1. Theme Management (Light / Dark Switcher)
    // -------------------------------------------------------------
    const THEME_STORAGE_KEY = "sdm_theme_preference";

    function getPreferredTheme() {
        const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
        if (storedTheme) {
            return storedTheme;
        }
        // Requirement 8.A: Pure white (#FFFFFF) default light theme
        return "light";
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(THEME_STORAGE_KEY, theme);

        const toggleBtn = document.getElementById("themeToggleBtn");
        if (toggleBtn) {
            if (theme === "dark") {
                toggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning me-1"></i> <span class="d-none d-sm-inline">Light</span>';
                toggleBtn.setAttribute("aria-label", "Switch to light mode");
                toggleBtn.title = "Switch to light mode";
            } else {
                toggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill text-secondary me-1"></i> <span class="d-none d-sm-inline">Dark</span>';
                toggleBtn.setAttribute("aria-label", "Switch to dark mode");
                toggleBtn.title = "Switch to dark mode";
            }
        }

        // Broadcast custom event so active Leaflet maps update their tile layers
        window.dispatchEvent(new CustomEvent("themeChanged", { detail: { theme: theme } }));
    }

    function initThemeToggle() {
        const initialTheme = getPreferredTheme();
        applyTheme(initialTheme);

        const toggleBtn = document.getElementById("themeToggleBtn");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", function () {
                const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
                const nextTheme = currentTheme === "dark" ? "light" : "dark";
                applyTheme(nextTheme);
            });
        }
    }

    // -------------------------------------------------------------
    // 2. Client-Side Form Validation & Interactivity
    // -------------------------------------------------------------
    function initFormValidation() {
        const reportForm = document.getElementById("incidentReportForm");
        if (!reportForm) return;

        reportForm.addEventListener("submit", function (e) {
            const title = document.getElementById("title");
            const disasterType = document.getElementById("disaster_type");
            const description = document.getElementById("description");
            const lat = document.getElementById("latitude");
            const lng = document.getElementById("longitude");
            const contact = document.getElementById("contact_number");

            let isValid = true;
            let errorMessages = [];

            if (!title || title.value.trim().length < 5) {
                isValid = false;
                errorMessages.push("Title must be at least 5 characters long.");
                title.classList.add("is-invalid");
            } else {
                title.classList.remove("is-invalid");
            }

            if (!disasterType || !disasterType.value) {
                isValid = false;
                errorMessages.push("Please select an emergency category.");
                disasterType.classList.add("is-invalid");
            } else {
                disasterType.classList.remove("is-invalid");
            }

            if (!description || description.value.trim().length < 15) {
                isValid = false;
                errorMessages.push("Please provide a description with at least 15 characters.");
                description.classList.add("is-invalid");
            } else {
                description.classList.remove("is-invalid");
            }

            if (!lat || !lng || !lat.value.trim() || !lng.value.trim()) {
                isValid = false;
                errorMessages.push("Please pick a location on the interactive map or enter valid coordinates.");
            }

            if (!contact || contact.value.trim().length < 7) {
                isValid = false;
                errorMessages.push("Please enter a valid emergency contact number.");
                contact.classList.add("is-invalid");
            } else {
                contact.classList.remove("is-invalid");
            }

            if (!isValid) {
                e.preventDefault();
                showClientAlert(errorMessages.join("<br>"), "danger");
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    }

    function showClientAlert(message, type = "danger") {
        const alertContainer = document.getElementById("clientAlertContainer");
        if (!alertContainer) return;

        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show alert-custom" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <div>${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }

    // -------------------------------------------------------------
    // 3. Document Ready Initialization
    // -------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", function () {
        initThemeToggle();
        initFormValidation();

        // Auto-dismiss bootstrap alerts after 7 seconds
        setTimeout(function () {
            const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
            alerts.forEach(function (alert) {
                const bsAlert = bootstrap.Alert.getInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            });
        }, 7000);
    });
})();
