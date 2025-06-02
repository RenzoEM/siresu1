const backendURL = "https://siresu1.onrender.com"; // Cambia si tienes otro

// LOGIN
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
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("¡Login exitoso!");
        if (data.role === "admin") {
          window.location.href = "admin.html";
        } else {
          window.location.href = "cliente.html";
        }
      } else {
        alert(data.message || "Credenciales incorrectas");
      }
    } catch (error) {
      alert("Error de conexión con el servidor");
      console.error("Error al hacer login:", error);
    }
  });
}

// REGISTRO
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const username = formData.get("username");
    const password = formData.get("password");

    try {
      const res = await fetch(`${backendURL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("¡Registro exitoso! Ahora inicia sesión.");
        window.location.href = "index.html";
      } else {
        alert(data.message || "Error al registrar");
      }
    } catch (error) {
      alert("Error de conexión con el servidor");
      console.error("Error al registrar:", error);
    }
  });
}

function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon = btn.querySelector("img");

  if (input.type === "password") {
    input.type = "text";
    icon.src = "eye-off.svg"; // Ícono de ojo tachado
  } else {
    input.type = "password";
    icon.src = "eye.svg"; // Ícono de ojo abierto
  }
}





