document.getElementById("uploadForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  fetch("/upload", {
    method: "POST",
    body: formData
  }).then(() => {
    alert("Upload complete. Click on video to define zones.");
  });
});

document.getElementById("video").addEventListener("click", function(e) {
  const rect = this.getBoundingClientRect();
  const x = Math.round(e.clientX - rect.left);
  const y = Math.round(e.clientY - rect.top);
  fetch("/click", {
    method: "POST",
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `x=${x}&y=${y}`
  });
});