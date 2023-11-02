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


document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("btn").addEventListener("click", async function() {
        let query = document.getElementById("query").value;
        let k = document.getElementById("k").value;

        let res = await fetch(`/api/search?query=${query}&k=${k}`);
        let data = await res.json();

        document.getElementById("execution-time").innerText = `${data.execution_time}`;  // Aquí es donde se actualiza el tiempo de ejecución

        let resultHTML = '';
        for (const item of data.content) {
            resultHTML += `
                <div class="result-item">
                    <span>ID: ${item[0]}</span>
                    <span>Descripción: ${item[1]}</span>
                    <span>Categoría: ${item[2]}</span>
                    <span>Puntuación: ${item[3]}</span>
                </div>
            `;
        }
        document.getElementById("result-box").innerHTML = resultHTML;
    });
});

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

            // Control de visibilidad para el tiempo de ejecución
            const executionTimeContainer = document.getElementById("execution-time-container");
            if (data.execution_time) {
                executionTimeContainer.style.display = "block";
                executionTimeContainer.innerText = `Tiempo de ejecución: ${data.execution_time}`;
            } else {
                executionTimeContainer.style.display = "none";
            }

            // Control de visibilidad para el contenedor de resultados
            const resultContainer = document.getElementById('resultContainer');
            if (data.content && data.content.length > 0) {
                resultContainer.style.display = "block";
                resultContainer.innerHTML = '';

                data.content.forEach(([id, name, content, rank]) => {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'result-item';

                    const nameProduct = document.createElement('p');
                    nameProduct.textContent = `Nombre: ${name}`;
                    resultItem.appendChild(nameProduct);

                    const contentElement = document.createElement('p');
                    contentElement.textContent = `Contenido: ${content}`;
                    resultItem.appendChild(contentElement);

                    const similitary = document.createElement('p');
                    similitary.textContent = `Similitary: ${rank}`;
                    resultItem.appendChild(similitary);

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
                resultContainer.style.display = "none";
            }

        } else {
            alert('Error al realizar la consulta');
        }
    } catch (error) {
        console.error('Hubo un problema con la operación fetch:', error);
    }
}
