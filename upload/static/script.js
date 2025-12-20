// Fetch and display work-in-progress tracks
// fetch from ./wips endpoint (returns JSON array of {title, artist, added})
document.addEventListener("DOMContentLoaded", () => {
  const wipDiv = document.getElementById("wips");

  fetch("./wips")
    .then((res) => res.json())
    .then((data) => {
      if (data["wips"].length === 0) {
        wipDiv.innerHTML = "The queue is empty /o/";
        return;
      }
      data["wips"].forEach((track) => {
        let text = track.title ?? "Unknown Title";
        if (track.from) {
          text = `${track.from} - ${text}`;
        } else if (track.artist) {
          text = `${track.artist} - ${text}`;
        }
        if (track.status) {
          text += ` (${track.status})`;
        }

        const trackDiv = document.createElement("li");
        trackDiv.appendChild(document.createTextNode(text));
        wipDiv.appendChild(trackDiv);
      });
    })
    .catch((err) => {
      console.error("Failed to fetch WIPs:", err);
      wipDiv.innerHTML = "<p>Failed to load work-in-progress tracks.</p>";
    });
});

// Have submit button be labelled "Send Suggestion" if no file inputs have any files,
// or "Start Upload" if there are files
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("upload-form");
  const submitButton = form.querySelector('button[type="submit"]');

  const updateButtonLabel = () => {
    const fileInputs = form.querySelectorAll('input[type="file"]');
    let hasFiles = false;
    fileInputs.forEach((input) => {
      if (input.files.length > 0) {
        hasFiles = true;
      }
    });
    submitButton.textContent = hasFiles ? "Start Upload" : "Send Suggestion";
  };

  form.addEventListener("change", updateButtonLabel);
  updateButtonLabel(); // Initial call to set the correct label
});

// Handle form submission with TUS resumable uploads
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("upload-form");
  const uploadsDiv = document.getElementById("uploads");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    uploadsDiv.innerHTML = "";

    // 1. Collect metadata (all non-file inputs)
    const formData = new FormData(form);
    const metadata = {};
    for (const [key, value] of formData.entries()) {
      const el = form.querySelector(`[name="${key}"]`);
      if (!el || el.type !== "file") {
        if (metadata[key]) {
          metadata[key].push(value);
        } else {
          metadata[key] = [value];
        }
      }
    }
    let url, body;

    // 2. Collect all files from any input[type="file"]
    const fileInputs = form.querySelectorAll('input[type="file"]');
    const files = [];
    fileInputs.forEach((input) => {
      Array.from(input.files).forEach((f) => files.push(f));
    });

    // 3. If there are files, do a file upload for /submit
    if (files.length > 0) {
      const res = await fetch("./session", { method: "POST" });
      const data = await res.json();
      const sessionId = data.session_id;

      const uploadPromises = files.map((file) => {
        return new Promise((resolve, reject) => {
          const row = document.createElement("div");
          row.className = "file-row";
          row.innerHTML = `<strong>${file.name}</strong><progress class="bar" value="0" max="100" />`;
          uploadsDiv.appendChild(row);
          const bar = row.querySelector(".bar");

          const upload = new tus.Upload(file, {
            endpoint: "./files/",
            metadata: { filename: file.name, session_id: sessionId },
            parallelUploads: 1,
            chunkSize: 5 * 1024 * 1024, // 5MB
            storeFingerprintForResuming: true,
            onProgress(bytesSent, bytesTotal) {
              console.log(`${file.name}: ${bytesSent}/${bytesTotal}`);
              bar.value = ((bytesSent / bytesTotal) * 100).toFixed(0);
            },
            onError(err) {
              console.error("Upload failed:", err);
              reject(err);
            },
            onSuccess(data) {
              console.log(data);
              bar.value = 100;
              resolve();
            },
          });
          upload.start();
        });
      });

      await Promise.all(uploadPromises);

      url = "./submit";
      body = { session_id: sessionId, tags: metadata };
    }
    // 4. If no files, just send metadata to /request
    else {
      url = "./request";
      body = { tags: metadata };
    }

    const finalizeRes = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const finalizeData = await finalizeRes.json();
    if (finalizeData.ok) {
      alert("Thank you, an admin should take a look at it soon <3");
    } else {
      alert(
        "There was an error processing your submission: " +
          (finalizeData.error || "Unknown error"),
      );
    }
    form.reset();
    uploadsDiv.innerHTML = "";
  });
});
