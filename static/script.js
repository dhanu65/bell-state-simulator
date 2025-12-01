document.getElementById("simulateBtn").addEventListener("click", async () => {
  const loadingOverlay = document.getElementById("loadingOverlay");
  const modal = document.getElementById("resultModal");
  const closeModal = document.getElementById("closeModal");

  const bellState = document.getElementById("bellState").value;
  const shots = document.getElementById("shots").value;

  loadingOverlay.style.display = "block";

  try {
    const response = await fetch(`/run_simulation?bell_state=${bellState}&shots=${shots}`);
    if (!response.ok) throw new Error("Simulation failed.");

    const data = await response.json();

    loadingOverlay.style.display = "none";
    modal.style.display = "block";

    window.results = {
      circuit: data.circuit_image,
      bloch: data.bloch_image,
      histogram: data.hist_image,
    };

    document.getElementById("state-text").innerText = data.statevector;

    // Enable buttons
    document.querySelectorAll(".view-btn").forEach((btn) => (btn.disabled = false));
    document.getElementById("downloadBtn").disabled = false;

    closeModal.addEventListener("click", () => {
      modal.style.display = "none";
    });
  } catch (error) {
    loadingOverlay.style.display = "none";
    alert("Error: " + error.message);
  }
});

document.querySelectorAll(".view-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (window.results) {
      document.getElementById("result-img").src = window.results[btn.dataset.img.split(".")[0]];
    }
  });
});

document.getElementById("downloadBtn").addEventListener("click", () => {
  if (!window.results) return;
  for (const key in window.results) {
    const link = document.createElement("a");
    link.href = window.results[key];
    link.download = key + ".png";
    link.click();
  }
});
