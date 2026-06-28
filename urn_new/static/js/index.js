const form = document.getElementById("urnForm");
const urnInput = document.getElementById("urn");
const errorDiv = document.getElementById("errorMessage");
const loadingOverlay = document.getElementById("loadingOverlay");
const searchBtn = document.getElementById("searchBtn");

form.addEventListener("submit", function (e) {

    const urn = urnInput.value.trim().toUpperCase();

    urnInput.value = urn;

    errorDiv.innerHTML = "";
    urnInput.classList.remove("error");

    if (urn.length < 18) {

        e.preventDefault();

        errorDiv.innerHTML = "URN must be at least 18 characters";

        urnInput.classList.add("error");

        return;
    }

    if (urn.length > 25) {

        e.preventDefault();

        errorDiv.innerHTML = "URN cannot be greater than 25 characters";

        urnInput.classList.add("error");

        return;
    }

    if (!(urn.startsWith("SB") || urn.startsWith("EIS"))) {

        e.preventDefault();

        errorDiv.innerHTML = "URN must start with SB or EIS";

        urnInput.classList.add("error");

        return;
    }

    loadingOverlay.style.display = "flex";

    searchBtn.disabled = true;

});