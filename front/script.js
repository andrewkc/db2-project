let imageMap = {};

async function loadImageMap() {
    try {
        const response = await fetch('https://raw.githubusercontent.com/johancalli/test/main/images.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        const rows = csvText.split('\n');
        rows.shift();
        rows.forEach(row => {
            const [filename, link] = row.split(',');
            const id = parseInt(filename.split('.')[0]);
            imageMap[id] = link;
        });
    } catch (error) {
        console.error('Ha ocurrido un error al cargar el CSV:', error);
    }
}

window.addEventListener('load', () => {
    loadImageMap();
});

const BASE_URL = "http://127.0.0.1:8000";

async function fetchData() {
    const query = document.getElementById('queryInput').value;
    const k = parseInt(document.getElementById('kInput').value);
    const method = document.getElementById('methodSelector').value;

    if (!query || isNaN(k)) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    const apiUrl = `${BASE_URL}${method}`;
    const payload = {
        query: query,
        k: k
    };

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            const data = await response.json();
            const resultContainer = document.getElementById('resultContainer');
            resultContainer.innerHTML = '';

            data.content.forEach(([id, name, content, rank]) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';

                const contentElement = document.createElement('p');
                contentElement.textContent = `Contenido: ${content}`;
                resultItem.appendChild(contentElement);

                if (imageMap[id]) {
                    const imageElement = document.createElement('img');
                    imageElement.src = imageMap[id];
                    imageElement.alt = `Imagen para ID ${id}`;
                    imageElement.width = 100; // o cualquier otro tamaño que prefieras
                    resultItem.appendChild(imageElement);
                }

                resultContainer.appendChild(resultItem);
            });
        } else {
            alert('Error al realizar la consulta');
        }
    } catch (error) {
        console.error('Hubo un problema con la operación fetch:', error);
    }
}
