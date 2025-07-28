// Función para inicializar el dropdown del usuario
function initUserDropdown() {
    const userIcon = document.getElementById('user-icon');
    const userDropdown = document.getElementById('user-dropdown');

    if (userIcon && userDropdown) {
        userIcon.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });

        // Cerrar el menú si se hace clic fuera de él
        document.addEventListener('click', (event) => {
            if (!userIcon.contains(event.target) && !userDropdown.contains(event.target)) {
                userDropdown.classList.remove('active');
            }
        });
    }
}

// Función para mostrar el selector de fecha 
function initDatePickers() {
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');

    if (checkinInput) {
        checkinInput.addEventListener('click', () => {
            checkinInput.showPicker();
        });
    }

    if (checkoutInput) {
        checkoutInput.addEventListener('click', () => {
            checkoutInput.showPicker();
        });
    }
}

// Función para manejar la búsqueda de alojamientos
function initSearch() {
    const searchButton = document.getElementById('search-button');
    if (searchButton) {
        searchButton.addEventListener('click', async e => {
            e.preventDefault();

            const fields = ['location', 'checkin', 'checkout', 'guests'];
            const data = Object.fromEntries(fields.map(id => [id, document.getElementById(id)?.value || '']));

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
    }
}

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
                <a href="/alojamiento/${a[0]}?checkin=${encodeURIComponent(document.getElementById('checkin')?.value || '')}&checkout=${encodeURIComponent(document.getElementById('checkout')?.value || '')}&guests=${encodeURIComponent(document.getElementById('guests')?.value || '')}">

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

    if (!checkinInput || !checkoutInput || !totalPriceDiv || !totalAmount) return;

    function calculateTotal() {
        const checkin = new Date(checkinInput.value);
        const checkout = new Date(checkoutInput.value);

        if (checkin && checkout && checkout > checkin) {
            const diffTime = checkout - checkin;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const total = diffDays * pricePerNight;

            totalAmount.textContent = '€' + total;
            totalPriceDiv.classList.remove('hidden');
        } else {
            totalAmount.textContent = '€0';
            totalPriceDiv.classList.add('hidden');
        }
    }

    checkinInput.addEventListener('change', calculateTotal);
    checkoutInput.addEventListener('change', calculateTotal);
    if (checkinInput.value && checkoutInput.value) {
        calculateTotal(); 
    }
}

// Inicializar todo cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initUserDropdown();
    initDatePickers();
    initSearch();
    
    // Inicializar cálculo de precio si estamos en la página de detalle
    const priceElement = document.querySelector('[data-price-per-night]');
    if (priceElement) {
        const pricePerNight = parseFloat(priceElement.dataset.pricePerNight);
        initPriceCalculation(pricePerNight);
    }
});



