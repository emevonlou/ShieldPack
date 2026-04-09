const button = document.getElementById("checkBtn");
const passwordInput = document.getElementById("password");
const resultBox = document.getElementById("result");

button.addEventListener("click", async () => {
  const password = passwordInput.value;

  resultBox.className = "result hidden";
  resultBox.textContent = "";

  if (!password.trim()) {
    resultBox.className = "result pwned";
    resultBox.textContent = "Digite uma senha para verificar.";
    return;
  }

  button.disabled = true;
  button.textContent = "Verificando...";

  try {
    const response = await fetch("/api/check-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ password })
    });

    const data = await response.json();

    resultBox.classList.remove("hidden");

    if (!response.ok) {
      resultBox.className = "result pwned";
      resultBox.textContent = data.detail || "Erro ao verificar a senha.";
      return;
    }

    if (data.pwned) {
      resultBox.className = "result pwned";
      resultBox.innerHTML = `
        <strong>Senha comprometida</strong><br>
        ${data.message}<br>
        <strong>Ocorrências:</strong> ${data.count}
      `;
    } else {
      resultBox.className = "result safe";
      resultBox.innerHTML = `
        <strong>Nenhum vazamento encontrado</strong><br>
        ${data.message}
      `;
    }
  } catch (error) {
    resultBox.className = "result pwned";
    resultBox.textContent = "Falha de conexão com a API.";
  } finally {
    button.disabled = false;
    button.textContent = "Verificar senha";
  }
});
