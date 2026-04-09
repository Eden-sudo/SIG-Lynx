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

// --- CÁMARA ---
UI.startBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        UI.video.srcObject = stream;
        UI.video.style.display = 'block';
        UI.imgOriginal.style.display = 'none';
        UI.startBtn.style.display = 'none';
        UI.captureBtn.style.display = 'inline-block';
        UI.stopBtn.style.display = 'inline-block';
    } catch (err) { alert("Error al activar cámara"); }
});

UI.captureBtn.addEventListener('click', () => {
    const ctx = UI.canvas.getContext('2d');
    UI.canvas.width = UI.video.videoWidth;
    UI.canvas.height = UI.video.videoHeight;
    ctx.drawImage(UI.video, 0, 0, UI.canvas.width, UI.canvas.height);
    
    UI.imgOriginal.src = UI.canvas.toDataURL('image/jpeg');
    UI.imgOriginal.style.display = 'block';
    UI.video.style.display = 'none';

    if (UI.video.srcObject) { UI.video.srcObject.getTracks().forEach(t => t.stop()); }

    UI.canvas.toBlob(async (blob) => {
        const fd = new FormData();
        fd.append("file", blob, "captura.jpg");
        await procesar(fd);
    }, 'image/jpeg');

    UI.captureBtn.style.display = 'none';
    UI.stopBtn.style.display = 'none';
    UI.startBtn.style.display = 'inline-block';
});

// --- SUBIDA MANUAL ---
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
            procesar(fd);
        };
        reader.readAsDataURL(file);
    }
});

// --- EL MOTOR ASÍNCRONO ---
async function procesar(formData) {
    try {
        console.log("🚀 Procesando...");
        const response = await fetch('/procesar', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok && data.status === "success") {
            // 1. Mostrar Imagen
            UI.imgResult.src = `/uploads/${data.archivo}?t=${new Date().getTime()}`;
            UI.downloadBtn.href = UI.imgResult.src;
            UI.downloadBtn.style.display = 'flex';

            // 2. Preparar Pizarrón
            UI.mathDashboard.style.display = 'block';
            UI.formulaContainer.innerHTML = ''; 

            // Resumen estadístico
            const info = document.createElement('div');
            info.style.color = "#f1c40f";
            info.style.marginBottom = "20px";
            info.innerHTML = `📝 <strong>Reporte:</strong> ${data.conteo} trazos analizados con éxito.`;
            UI.formulaContainer.appendChild(info);

            // Renderizado por partes (Paginación)
            const limite = 5;
            const renderEq = (eq, i) => {
                const div = document.createElement('div');
                div.style.padding = "10px";
                div.style.borderBottom = "1px solid #333";
                katex.render(`P_{${i+1}}(t): ${eq}`, div, { displayMode: true });
                UI.formulaContainer.appendChild(div);
            };

            // Mostrar las primeras 5 de golpe
            data.ecuaciones.slice(0, limite).forEach((eq, i) => renderEq(eq, i));

            // Botón para cargar el resto
            if (data.ecuaciones.length > limite) {
                const btn = document.createElement('button');
                btn.innerText = `➕ Ver las ${data.ecuaciones.length - limite} restantes`;
                btn.className = "btn-main btn-secondary";
                btn.style.width = "100%";
                btn.onclick = () => {
                    btn.remove();
                    data.ecuaciones.slice(limite).forEach((eq, i) => {
                        // Delay de 10ms para no congelar el navegador
                        setTimeout(() => renderEq(eq, i + limite), i * 10);
                    });
                };
                UI.formulaContainer.appendChild(btn);
            }
        } else { alert("Error: " + data.detalle); }
    } catch (e) { console.error(e); }
}
