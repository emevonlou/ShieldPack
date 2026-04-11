const passwordBtn = document.getElementById("checkPasswordBtn");
const emailBtn = document.getElementById("checkEmailBtn");

const passwordInput = document.getElementById("password");
const emailInput = document.getElementById("email");

const resultBox = document.getElementById("result");

// 🔐 SENHA
passwordBtn.addEventListener("click", async () => {
  const password = passwordInput.value;

  if (!password.trim()) {
    showError("Digite uma senha.");
    return;
  }

  setLoading(passwordBtn);

  try {
    const res = await fetch("/api/check-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });

    const data = await res.json();

    if (data.pwned) {
      showError(`⚠️ Senha comprometida (${data.count} vezes)`);
    } else {
      showSuccess("✅ Senha segura (não encontrada)");
    }

  } catch {
    showError("Erro ao verificar senha.");
  }

  resetButton(passwordBtn, "Verificar senha");
});

// ✉️ EMAIL
emailBtn.addEventListener("click", async () => {
  const email = emailInput.value;

  if (!email.trim()) {
    showError("Digite um e-mail.");
    return;
  }

  setLoading(emailBtn);

  try {
    const res = await fetch("/api/check-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    const data = await res.json();

    if (data.found) {
      showError(`
         Encontrado em ${data.breaches.length} vazamento(s)<br>
        ${data.breaches.join(", ")}
      `);
    } else {
      showSuccess(data.message);
    }

  } catch {
    showError("Erro ao verificar e-mail.");
  }

  resetButton(emailBtn, "Verificar e-mail");
});

// UI helpers
function showError(msg) {
  resultBox.className = "result pwned";
  resultBox.innerHTML = msg;
  resultBox.classList.remove("hidden");
}

function showSuccess(msg) {
  resultBox.className = "result safe";
  resultBox.innerHTML = msg;
  resultBox.classList.remove("hidden");
}

function setLoading(btn) {
  btn.disabled = true;
  btn.textContent = "Verificando...";
}

function resetButton(btn, text) {
  btn.disabled = false;
  btn.textContent = text;
}
