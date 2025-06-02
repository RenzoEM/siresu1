const backendURL = "https://siresu1.onrender.com"; // o http://localhost:5000

const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const username = formData.get("username");
    const password = formData.get("password");

    try {
      const res = await fetch(`${backendURL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if (res.ok) {
        // Redirige según el rol del usuario
        if (data.role === "admin") {
          window.location.href = "admin.html";
        } else {
          window.location.href = "cliente.html";
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Error de conexión");
      console.error(error);
    }
  });
}

// Mostrar lista de usuarios en admin.html
const userTable = document.getElementById("user-list");
if (userTable) {
  fetch(`${backendURL}/users`)
    .then(res => res.json())
    .then(users => {
      userTable.innerHTML = users.map(u => `
        <tr>
          <td>${u.id}</td>
          <td>${u.username}</td>
          <td>${u.role}</td>
          <td>-</td>
        </tr>
      `).join('');
    });
}

// Crear nuevo admin desde el formulario
const adminForm = document.getElementById("admin-create-form");
if (adminForm) {
  adminForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${backendURL}/create-admin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: email, password })
    });

    const data = await res.json();
    alert(data.message);
    if (res.ok) location.reload();
  });
}

