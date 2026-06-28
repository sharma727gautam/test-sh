// =========================
// TAB SWITCHING
// =========================

function showTab(event, tabId) {

    const tabs = document.querySelectorAll(".tab-content");

    tabs.forEach(function(tab) {

        tab.style.display = "none";

    });

    document.getElementById(tabId).style.display = "block";


    const buttons = document.querySelectorAll(".tab-button");

    buttons.forEach(function(btn) {

        btn.classList.remove("active");

    });

    event.currentTarget.classList.add("active");

}


// =========================
// RECORD EXPAND / COLLAPSE
// =========================

function toggleRecord(header) {

    const body = header.nextElementSibling;

    const icon = header.querySelector(".expand-icon");

    if (body.style.display === "none" || body.style.display === "") {

        body.style.display = "grid";

        icon.innerHTML = "▲";

    }

    else {

        body.style.display = "none";

        icon.innerHTML = "▼";

    }

}


// =========================
// MODAL
// =========================

let currentPayload = "";

function openModal(title, text) {

    currentPayload = text;

    document.getElementById("modalTitle").innerText = title;

    document.getElementById("modalBody").innerText = text;

    document.getElementById("payloadModal").style.display = "block";

}

function closeModal() {

    document.getElementById("payloadModal").style.display = "none";

}


// =========================
// COPY BUTTONS
// =========================

function miniCopy(button, text) {

    navigator.clipboard.writeText(text);

    const original = button.innerHTML;

    button.innerHTML = "✔";

    setTimeout(function() {

        button.innerHTML = original;

    }, 1500);

}


document.addEventListener("DOMContentLoaded", function () {

    const copyBtn = document.getElementById("copyModalBtn");

    if (copyBtn) {

        copyBtn.onclick = function () {

            navigator.clipboard.writeText(currentPayload);

            const original = copyBtn.innerHTML;

            copyBtn.innerHTML = "✔ Copied";

            setTimeout(function () {

                copyBtn.innerHTML = original;

            }, 1500);

        };

    }

});


// =========================
// CLOSE MODAL ON BACKGROUND
// =========================

window.onclick = function(event) {

    const modal = document.getElementById("payloadModal");

    if (event.target === modal) {

        closeModal();

    }

};