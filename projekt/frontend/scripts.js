const token = localStorage.getItem("token");

function getStatus(lastSeen) {
    const diff = (new Date() - new Date(lastSeen)) / 1000;

    if (diff < 15) return "online";
    if (diff < 60) return "unknown";
    return "offline";
}

async function load() {
    const res = await fetch("http://127.0.0.1:8000/clients", {
        headers: {
            Authorization: "Bearer " + token
        }
    });

    if (res.status === 401) {
        location.href = "login.html";
        return;
    }

    const data = await res.json();

    let html = "";

    data.forEach(c => {
        const s = getStatus(c.last_seen);

        html += `
        <tr>
            <td>${c.hostname}</td>
            <td>${c.ip_address}</td>
            <td class="${s}">${s}</td>
            <td>${c.last_seen}</td>
        </tr>`;
    });

    document.getElementById("table").innerHTML = html;
}

setInterval(load, 3000);
load();