var offcanvasSidebar = document.getElementById("offcanvasSidebar");
var activationButton = document.querySelector("[data-bs-target='#offcanvasSidebar']");

offcanvasSidebar.addEventListener("show.bs.offcanvas", function () {
  activationButton.classList.add("d-none");
});

offcanvasSidebar.addEventListener("hidden.bs.offcanvas", function () {
  activationButton.classList.remove("d-none");
});