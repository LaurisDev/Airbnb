//Despligue
const userIcon = document.getElementById('user-icon');
        const userDropdown = document.getElementById('user-dropdown');

        userIcon.addEventListener('click', () => {
            userDropdown.classList.toggle('active');
        });

        // Cerrar el menú si se hace clic fuera de él
        window.addEventListener('click', (event) => {
            if (!userIcon.contains(event.target) && !userDropdown.contains(event.target)) {
                userDropdown.classList.remove('active');
            }
        });

// Función para mostrar el selector de fecha
document.getElementById('checkin').addEventListener('click', () => {
    document.getElementById('checkin').showPicker();
});

document.getElementById('checkout').addEventListener('click', () => {
    document.getElementById('checkout').showPicker();
});


// Función para manejar la búsqueda de alojamientos
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('search-button').addEventListener('click', async e => {
        e.preventDefault();

        const fields = ['location', 'checkin', 'checkout', 'guests'];
        const data = Object.fromEntries(fields.map(id => [id, document.getElementById(id).value]));

        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const results = await response.json();
            updateSearchResults(results);
        } catch (err) {
            console.error('Error al buscar:', err);
            alert('Ocurrió un error al buscar alojamientos.');
        }
    });
});

function updateSearchResults(results) {
    const container = document.querySelector('.grid');
    container.innerHTML = results.length === 0
        ? '<p>No se encontraron alojamientos con esos criterios.</p>'
        : results.map(a => `
            <div class="property-card bg-white rounded-xl overflow-hidden shadow-md hover:shadow-lg transition duration-300">
                <div class="relative">
                    <img src="${a[3]}" alt="${a[1]}" class="w-full h-48 object-cover" loading="lazy"
                        onerror="this.onerror=null;this.src='https://i.gifer.com/ZZ5H.gif';this.style.width='64px';this.style.height='64px';this.style.objectFit='contain';">
                    <button class="absolute top-3 right-3 heart-hover"></button>
                </div>
                <div class="p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-lg">${a[0]}</h3>
                            <p class="text-gray-500">${a[1]}</p>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-star text-sm text-rose-500"></i>
                            <span class="ml-1 text-sm">${a[4]}</span>
                        </div>
                    </div>
                    <p class="mt-2 text-gray-700"><span class="font-semibold">€${a[2]}</span> noche</p>
                </div>
            </div>
        `).join('');
}
