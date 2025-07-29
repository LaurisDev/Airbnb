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



