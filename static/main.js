document.addEventListener('DOMContentLoaded', function () {
    const authButtons = document.getElementById('auth-buttons');
    const loggedInUser = localStorage.getItem('username'); // Замените на серверный механизм или куки

    if (loggedInUser) {
        authButtons.innerHTML = `
            <a href="/profile/${loggedInUser}" class="user-button">${loggedInUser}</a>
            <button class="logout-button" onclick="logout()">Выйти</button>
        `;
    }

    const buttons = document.querySelectorAll('button');

    buttons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            const targetUrl = event.target.dataset.url;
            if (targetUrl) {
                window.location.href = targetUrl;
            }
        });
    });
});

// Функция выхода
function logout() {
    window.location.href = "/logout"; // Переход на маршрут выхода
}