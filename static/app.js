// Canvas setup
const canvas = document.getElementById('sunCanvas');
const ctx = canvas.getContext('2d');
let gridSize = 16;
let visualMode = 'bit';
let solarData = null;

function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
}

function drawSun() {
    if (!solarData) return;

    const width = canvas.width / window.devicePixelRatio;
    const height = canvas.height / window.devicePixelRatio;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 10;

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, width, height);

    const cellSize = (radius * 2) / gridSize;

    ctx.save();
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.clip();

    for (let row = 0; row < gridSize; row++) {
        for (let col = 0; col < gridSize; col++) {
            const x = centerX - radius + col * cellSize;
            const y = centerY - radius + row * cellSize;

            const solarX = (col - gridSize / 2) / (gridSize / 2);
            const solarY = (row - gridSize / 2) / (gridSize / 2);
            const dist = Math.sqrt(solarX * solarX + solarY * solarY);

            if (dist <= 1 && solarData.regions) {
                let intensity = 0;

                for (const spot of solarData.regions) {
                    const lonRad = (spot.lon - 180) * Math.PI / 180;
                    const latRad = spot.lat * Math.PI / 180;
                    const spotX = Math.sin(lonRad) * Math.cos(latRad);
                    const spotY = Math.sin(latRad);
                    const cellDist = Math.sqrt(
                        Math.pow(spotX - solarX, 2) + Math.pow(spotY - solarY, 2)
                    );

                    if (cellDist < 0.15) {
                        if (visualMode === 'bit') {
                            intensity = 1;
                        } else if (visualMode === 'linear') {
                            intensity = Math.max(intensity, spot.intensity);
                        } else {
                            intensity = Math.max(intensity, spot.intensity * (1 - cellDist / 0.15));
                        }
                    }
                }

                if (intensity > 0) {
                    if (visualMode === 'bit') {
                        ctx.fillStyle = '#fff';
                    } else {
                        ctx.fillStyle = `rgba(255,255,255,${intensity})`;
                    }
                    ctx.fillRect(x, y, cellSize - 1, cellSize - 1);
                }
            }
        }
    }

    ctx.restore();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.stroke();
}

function updateTime() {
    const now = new Date();
    document.getElementById('utc-time').textContent = now.toUTCString().split(' ')[4];
}

function updateDisplay() {
    if (!solarData) return;

    const regionList = document.getElementById('region-list');
    regionList.innerHTML = '';
    if (solarData.regions && solarData.regions.length) {
        solarData.regions.forEach(r => {
            const item = document.createElement('div');
            item.className = 'region-item';
            item.innerHTML = `<span>AR${r.noaa_number}</span><span>${r.area} MSH</span>`;
            regionList.appendChild(item);
        });
    } else {
        regionList.innerHTML = '<div style="opacity:0.5">No active regions</div>';
    }

    document.getElementById('region-count').textContent = solarData.active_region_count || 0;
    document.getElementById('solar-flux').textContent = solarData.solar_flux?.toFixed(1) ?? '---';
    document.getElementById('xray-flux').textContent = solarData.xray_class || '---';
    document.getElementById('solar-wind').textContent = solarData.solar_wind_speed ? Math.floor(solarData.solar_wind_speed) : '---';
    document.getElementById('kp-index').textContent = solarData.kp_index ?? '-';
}

async function fetchData() {
    try {
        const resp = await fetch('/api/solar-data');
        if (resp.ok) {
            solarData = await resp.json();
            updateDisplay();
            drawSun();
        }
    } catch (err) {
        console.error('Failed to fetch data', err);
    }
}

document.querySelectorAll('.toggle[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.toggle[data-mode]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        visualMode = btn.dataset.mode;
        drawSun();
    });
});

document.getElementById('grid-slider').addEventListener('input', e => {
    gridSize = parseInt(e.target.value, 10);
    document.getElementById('grid-value').textContent = gridSize;
    drawSun();
});

window.addEventListener('resize', resizeCanvas);

resizeCanvas();
updateTime();
setInterval(updateTime, 1000);
fetchData();
setInterval(fetchData, 30000);

