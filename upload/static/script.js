document.addEventListener("DOMContentLoaded", () => {
  const wipDiv = document.getElementById("wips");

  // Fetch and display work-in-progress tracks
  // fetch from ./wips endpoint (returns JSON array of {title, artist, added})
  fetch("./wips")
    .then((res) => res.json())
    .then((data) => {
      if (data["wips"].length === 0) {
        wipDiv.innerHTML = "The queue is empty /o/";
        return;
      }
      data["wips"].forEach((track) => {
        const trackDiv = document.createElement("div");
        trackDiv.className = "wip-track";
        const strong = document.createElement("strong");
        strong.textContent = track.title;
        trackDiv.appendChild(strong);
        const byText = document.createTextNode(` by ${track.artist}`);
        trackDiv.appendChild(byText);
        wipDiv.appendChild(trackDiv);
      });
    })
    .catch((err) => {
      console.error("Failed to fetch WIPs:", err);
      wipDiv.innerHTML = "<p>Failed to load work-in-progress tracks.</p>";
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("upload-form");
  const uploadsDiv = document.getElementById("uploads");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    uploadsDiv.innerHTML = "";

    let sessionId = null;

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

    // 2. Collect all files from any input[type="file"]
    const fileInputs = form.querySelectorAll('input[type="file"]');
    const files = [];
    fileInputs.forEach((input) => {
      Array.from(input.files).forEach((f) => files.push(f));
    });

    // 3. Create session only if there are files to upload
    if (files.length > 0) {
      const res = await fetch("./session", { method: "POST" });
      const data = await res.json();
      sessionId = data.session_id;

      // 4. Upload files in parallel
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
    } else {
      // If no files, just create a session id for metadata storage
      const res = await fetch("./session", { method: "POST" });
      const data = await res.json();
      sessionId = data.session_id;
    }

    // 5. Finalize metadata (and files if any)
    const finalizePayload = {
      session_id: sessionId,
      tags: metadata,
    };

    const finalizeRes = await fetch("./finalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(finalizePayload),
    });

    //const finalizeData = await finalizeRes.json();
    alert("Thank you, an admin should take a look at it soon <3");
    form.reset();
    uploadsDiv.innerHTML = "";
  });
});
