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

document.getElementById('checkin').addEventListener('click', () => {
    document.getElementById('checkin').showPicker();
});

document.getElementById('checkout').addEventListener('click', () => {
    document.getElementById('checkout').showPicker();
});