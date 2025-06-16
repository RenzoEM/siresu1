const backendURL = "https://siresu1.onrender.com";

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
        window.location.href = data.role === "admin" ? "admin.html" : "cliente.html";
      } else {
        alert(data.message || "Error al iniciar sesión");
      }
    } catch (error) {
      console.error("Error en login:", error);
      alert("Error de conexión con el servidor");
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
        alert("¡Registro exitoso!");
        window.location.href = "index.html";
      } else {
        alert(data.message || "Error al registrar");
      }
    } catch (error) {
      console.error("Error en registro:", error);
      alert("Error de conexión con el servidor");
    }
  });
}
