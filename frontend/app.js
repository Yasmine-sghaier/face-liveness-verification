const video = document.getElementById("video");
const button = document.getElementById("capture");

// 1. Demander accès à la caméra
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => console.error("Erreur caméra:", err));

button.addEventListener("click", () => {
  // 2. Capturer la photo dans un canvas
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // 3. Convertir en blob et envoyer à FastAPI
  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append("file", blob, "live.png"); // doit matcher le paramètre FastAPI

    try {
      const response = await fetch("http://127.0.0.1:8000/verify", {
        method: "POST",
        body: formData
      });
      const result = await response.json();
      console.log("Résultat:", result);
      alert(JSON.stringify(result));
    } catch (err) {
      console.error("Erreur fetch:", err);
    }
  }, "image/png");
});