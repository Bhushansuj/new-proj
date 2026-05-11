function getStatus(lastUpdate) {
    const now = new Date();
    const last = new Date(lastUpdate);

    const diff = (now - last) / 1000;

    if (diff < 15) return "online";
    if (diff < 60) return "unknown";
    return "offline";
}

function statusBadge(status) {
    return `<span class="status ${status}">${status.toUpperCase()}</span>`;
}

async function loadData() {
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/clients", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "login.html";
            return;
        }

        if (!res.ok) {
            console.error("Error:", res.status);
            return;
        }

        const data = await res.json();

        let html = "";
        let online = 0;
        let offline = 0;

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(c => {
                const status = getStatus(c.last_update);

                if (status === "online") online++;
                else if (status === "offline") offline++;

                html += `
                <tr>
                    <td>${c.hostname}</td>
                    <td>${c.mac_address || "N/A"}</td>
                    <td>${statusBadge(status)}</td>
                    <td>${new Date(c.last_update).toLocaleString()}</td>
                </tr>
                `;
            });
        }

        document.getElementById("table").innerHTML = html || "<tr><td colspan='4'>No devices</td></tr>";
        document.getElementById("onlineCount").innerText = online;
        document.getElementById("offlineCount").innerText = offline;
        document.getElementById("totalCount").innerText = data.length || 0;
    } catch (error) {
        console.error("Error:", error);
    }
}

setInterval(loadData, 3000);
loadData();
