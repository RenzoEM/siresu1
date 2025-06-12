const backendURL = "https://siresu1.onrender.com";

// LOGIN
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = loginForm.username.value.trim();
    const password = loginForm.password.value.trim();

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
    } catch (err) {
      alert("Error de conexión con el servidor");
      console.error("Error en login:", err);
    }
  });
}

// REGISTRO
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = registerForm.username.value.trim();
    const password = registerForm.password.value.trim();

    try {
      const res = await fetch(`${backendURL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (res.ok) {
        alert("¡Registro exitoso!");
        window.location.href = "index.html";
      } else {
        alert(data.message || "Error al registrar");
      }
    } catch (err) {
      alert("Error de conexión con el servidor");
      console.error("Error en registro:", err);
    }
  });
}
