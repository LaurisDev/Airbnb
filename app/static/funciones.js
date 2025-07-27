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


// Función para manejar la búsqueda de alojamientos (movida a DOMContentLoaded)


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
    if (!container) {
        console.error('No se encontró el contenedor .grid');
        return;
    }

    container.innerHTML = results.length === 0
        ? '<p>No se encontraron alojamientos con esos criterios.</p>'
        : results.map(a => `
            <div class="property-card bg-white rounded-xl overflow-hidden shadow-md hover:shadow-lg transition duration-300">
                <a href="/alojamiento/${a[0]}?checkin=${encodeURIComponent(document.getElementById('checkin').value)}&checkout=${encodeURIComponent(document.getElementById('checkout').value)}&guests=${encodeURIComponent(document.getElementById('guests').value)}">

               <div class="relative">
                    <img src="${a[4]}" alt="${a[1]}" class="w-full h-48 object-cover" loading="lazy"
                        onerror="this.onerror=null;this.src='https://i.gifer.com/ZZ5H.gif';this.style.width='64px';this.style.height='64px';this.style.objectFit='contain';">
                    <button class="absolute top-3 right-3 heart-hover"></button>
                </div>
                <div class="p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="font-bold text-lg">${a[1]}</h3>
                            <p class="text-gray-500">${a[2]}</p>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-star text-sm text-rose-500"></i>
                            <span class="ml-1 text-sm">${a[5]}</span>
                        </div>
                    </div>
                    <p class="mt-2 text-gray-700"><span class="font-semibold">€${a[3]}</span> noche</p>
                </div>
            </div>
        `).join('');
}

// Función para calcular el precio total de la reserva
function initPriceCalculation(pricePerNight) {
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    const totalPriceDiv = document.getElementById('total-price');
    const totalAmount = document.getElementById('total-amount');

    if (!checkinInput || !checkoutInput || !totalPriceDiv || !totalAmount) {
        return; // Si no estamos en la página de detalles, salir
    }

    function calculateTotal() {
        const checkinIso = checkinInput.getAttribute('data-iso-date');
        const checkoutIso = checkoutInput.getAttribute('data-iso-date');
        
        if (checkinIso && checkoutIso) {
            const checkin = new Date(checkinIso);
            const checkout = new Date(checkoutIso);
            
            if (checkout > checkin) {
                const diffTime = Math.abs(checkout - checkin);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                const total = diffDays * pricePerNight;
                
                totalAmount.textContent = '€' + total;
                totalPriceDiv.classList.remove('hidden');
            } else {
                totalPriceDiv.classList.add('hidden');
            }
        } else {
            totalPriceDiv.classList.add('hidden');
        }
    }

    checkinInput.addEventListener('change', calculateTotal);
    checkoutInput.addEventListener('change', calculateTotal);
}

