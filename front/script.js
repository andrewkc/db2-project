async function fetchData() {
    const query = document.getElementById("queryInput").value;
    const k = parseInt(document.getElementById("kInput").value);
    const method = document.getElementById("methodSelector").value;

    try {
        const response = await fetch(method, {
            method: 'POST',
            body: JSON.stringify({ query: query, k: k }),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        document.getElementById("data").innerText = JSON.stringify(data.content, null, 2);

    } catch (error) {
        console.error("Hubo un error al recuperar los datos:", error);
    }
}

async function createIndex() {
    try {
        const response = await fetch('/create_index', { method: 'POST' });
        const result = await response.json();

        if (result.response === 200) {
            alert("Índice creado exitosamente.");
        } else {
            alert("Error al crear el índice.");
        }
    } catch (error) {
        console.error("Hubo un error al crear el índice:", error);
    }
}
