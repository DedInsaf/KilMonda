document.getElementById('registrationForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/registration/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
        alert('Registration successful!');
    } else {
        const result = await response.json();
        alert(`Registration failed: ${result.detail}`);
    }
});
