const UI = {
    video: document.getElementById('webcam'),
    canvas: document.getElementById('captureCanvas'),
    imgOriginal: document.getElementById('imgOriginal'),
    imgResult: document.getElementById('imgResult'),
    startBtn: document.getElementById('startBtn'),
    captureBtn: document.getElementById('captureBtn'),
    stopBtn: document.getElementById('stopBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    imageInput: document.getElementById('imageInput'),
    mathDashboard: document.getElementById('mathDashboard'),
    formulaContainer: document.getElementById('formulaContainer')
};

// --- Camera Control ---
UI.startBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        UI.video.srcObject = stream;
        UI.video.style.display = 'block';
        UI.imgOriginal.style.display = 'none';
        UI.startBtn.style.display = 'none';
        UI.captureBtn.style.display = 'inline-block';
        UI.stopBtn.style.display = 'inline-block';
    } catch (err) { 
        console.error("Camera access denied:", err);
        alert("Error: Unable to access camera."); 
    }
});

UI.captureBtn.addEventListener('click', () => {
    const ctx = UI.canvas.getContext('2d');
    UI.canvas.width = UI.video.videoWidth;
    UI.canvas.height = UI.video.videoHeight;
    ctx.drawImage(UI.video, 0, 0, UI.canvas.width, UI.canvas.height);
    
    UI.imgOriginal.src = UI.canvas.toDataURL('image/jpeg');
    UI.imgOriginal.style.display = 'block';
    UI.video.style.display = 'none';

    if (UI.video.srcObject) { 
        UI.video.srcObject.getTracks().forEach(t => t.stop()); 
    }

    UI.canvas.toBlob(async (blob) => {
        const fd = new FormData();
        fd.append("file", blob, "capture.jpg");
        await processRequest(fd);
    }, 'image/jpeg');

    UI.captureBtn.style.display = 'none';
    UI.stopBtn.style.display = 'none';
    UI.startBtn.style.display = 'inline-block';
});

// --- Manual Upload ---
UI.imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (ev) => {
            UI.imgOriginal.src = ev.target.result;
            UI.imgOriginal.style.display = 'block';
            UI.video.style.display = 'none';
            const fd = new FormData();
            fd.append("file", file);
            processRequest(fd);
        };
        reader.readAsDataURL(file);
    }
});

// --- Async Core Logic ---
async function processRequest(formData) {
    try {
        console.log("[Client] Processing request...");
        const response = await fetch('/procesar', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok && data.status === "success") {
            // 1. Result Visualization
            UI.imgResult.src = `/uploads/${data.archivo}?t=${new Date().getTime()}`;
            UI.downloadBtn.href = UI.imgResult.src;
            UI.downloadBtn.style.display = 'flex';

            // 2. Dashboard Update
            UI.mathDashboard.style.display = 'block';
            UI.formulaContainer.innerHTML = ''; 

            // Summary Report
            const info = document.createElement('div');
            info.style.color = "#f1c40f";
            info.style.marginBottom = "20px";
            info.innerHTML = `<strong>Analysis Report:</strong> ${data.conteo} vectors successfully mapped.`;
            UI.formulaContainer.appendChild(info);

            // Progressive Rendering logic
            const limit = 5;
            const renderEq = (eq, i) => {
                const div = document.createElement('div');
                div.style.padding = "10px";
                div.style.borderBottom = "1px solid #333";
                // KaTeX rendering for parametric equations
                katex.render(`P_{${i+1}}(t): ${eq}`, div, { displayMode: true });
                UI.formulaContainer.appendChild(div);
            };

            // Render first batch
            data.ecuaciones.slice(0, limit).forEach((eq, i) => renderEq(eq, i));

            // Load Remaining Button
            if (data.ecuaciones.length > limit) {
                const btn = document.createElement('button');
                btn.innerText = `View remaining ${data.ecuaciones.length - limit} equations`;
                btn.className = "btn-main btn-secondary";
                btn.style.width = "100%";
                btn.onclick = () => {
                    btn.remove();
                    data.ecuaciones.slice(limit).forEach((eq, i) => {
                        // 10ms timeout to prevent browser UI freezing
                        setTimeout(() => renderEq(eq, i + limit), i * 10);
                    });
                };
                UI.formulaContainer.appendChild(btn);
            }
        } else { 
            alert("Error: " + data.detalle); 
        }
    } catch (e) { 
        console.error("Processing failed:", e); 
    }
}
