let imageMap = {};

async function loadImageMap() {
    try {
        // Reemplaza con tu URL "raw" de GitHub
        const response = await fetch('https://raw.githubusercontent.com/johancalli/test/main/images.csv'); 
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        console.log('CSV Text:', csvText);  // Agregado para depuración
        const rows = csvText.split('\n');
        rows.shift(); // Eliminar la primera fila (encabezados)
        rows.forEach(row => {
            const [filename, link] = row.split(',');
            const id = parseInt(filename.split('.')[0]); 
            imageMap[id] = link;
        });
        console.log('Image map loaded:', imageMap);  // Agregado para depuración
    } catch (error) {
        console.error('Ha ocurrido un error al cargar el CSV:', error);
    }
}


window.addEventListener('load', () => {
    loadImageMap();
});

const BASE_URL = "http://127.0.0.1:8000";

// Función para obtener datos desde la API y mostrarlos
async function fetchData() {
    const query = document.getElementById('queryInput').value;
    const k = parseInt(document.getElementById('kInput').value); // Convertir a entero
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
            resultContainer.innerHTML = ''; // Limpiar resultados anteriores
            
            let displayedResults = 0; // Contador para saber cuántos resultados se han mostrado

            data.content.forEach(([id, description]) => {
                if (displayedResults >= k) {
                    return; // Detener el loop si ya hemos mostrado k resultados
                }

                const imageLink = imageMap[id];
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';

                if (imageLink) {
                    const imgElement = document.createElement('img');
                    imgElement.src = imageLink;
                    imgElement.alt = `Imagen de ID ${id}`;
                    imgElement.style.maxWidth = "200px";  // Redimensionar la imagen si es necesario
                    imgElement.style.maxHeight = "200px";  // Redimensionar la imagen si es necesario
                    resultItem.appendChild(imgElement);
                }

                const descriptionElement = document.createElement('p');
                descriptionElement.textContent = description;
                resultItem.appendChild(descriptionElement);

                resultContainer.appendChild(resultItem);
                
                displayedResults++;  // Incrementar el contador de resultados mostrados
            });
        } else {
            alert('Error al realizar la consulta');
        }
    } catch (error) {
        console.error('Hubo un problema con la operación fetch:', error);
    }
}

