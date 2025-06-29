document.getElementById("uploadForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const formData = new FormData(this);

  fetch("/upload", {
    method: "POST",
    body: formData
  }).then((response) => {
    if (response.ok) {
      document.getElementById("statusMessage").innerText = "✅ Upload complete! Click on the video to define zones.";
      const video = document.getElementById("video");
      video.src = "/video_feed?" + new Date().getTime(); // force refresh
      video.style.display = "block"; // show video after upload
    } else {
      document.getElementById("statusMessage").innerText = "❌ Upload failed.";
    }
  }).catch((error) => {
    document.getElementById("statusMessage").innerText = "❌ Error uploading file.";
    console.error("Upload error:", error);
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
  }).then((response) => {
    if (response.ok) {
      console.log(`✅ Clicked at (${x}, ${y})`);
    } else {
      console.error("❌ Failed to send click coordinates.");
    }
  });
});
