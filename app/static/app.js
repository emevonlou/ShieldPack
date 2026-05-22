const passwordBtn = document.getElementById("checkPasswordBtn");
const emailBtn = document.getElementById("checkEmailBtn");

const passwordInput = document.getElementById("password");
const emailInput = document.getElementById("email");

const resultBox = document.getElementById("result");

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

    if (!res.ok) {
      showError(data.detail || "Erro ao verificar senha.");
      return;
    }

    showPasswordResult(data);
  } catch {
    showError("Erro ao verificar senha.");
  }

  resetButton(passwordBtn, "Verificar senha");
});

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

    if (!res.ok) {
      showError(data.detail || "Erro ao verificar e-mail.");
      return;
    }

    if (data.found) {
      showError(`
        <strong>⚠️ E-mail exposto</strong><br>
        Encontrado em ${data.breaches.length} vazamento(s).<br>
        ${data.breaches.join(", ")}
      `);
    } else {
      showSuccess(`<strong>ℹ️ E-mail</strong><br>${data.message}`);
    }
  } catch {
    showError("Erro ao verificar e-mail.");
  }

  resetButton(emailBtn, "Verificar e-mail");
});

function showPasswordResult(data) {
  const badge = getRiskBadge(data.risk_level);

  const html = `
    <div class="risk-header">
      <span class="risk-icon">${badge.icon}</span>
      <div>
        <strong>${badge.title}</strong>
        <p>${badge.subtitle}</p>
      </div>
    </div>

    <div class="risk-meter">
      <div class="risk-meter-fill ${data.risk_level}"></div>
    </div>

    <p>${data.message}</p>

    <div class="recommendation">
      <strong>Recomendação:</strong><br>
      ${data.recommendation}
    </div>
  `;

  if (data.risk_level === "low") {
    showSuccess(html);
  } else {
    showError(html);
  }
}

function getRiskBadge(level) {
  if (level === "high") {
    return {
      icon: "🔴",
      title: "Alto risco",
      subtitle: "Esta senha deve ser trocada imediatamente."
    };
  }

  if (level === "medium") {
    return {
      icon: "🟠",
      title: "Médio risco",
      subtitle: "Esta senha já apareceu em vazamentos."
    };
  }

  return {
    icon: "🟢",
    title: "Baixo risco",
    subtitle: "Nenhum vazamento encontrado na base consultada."
  };
}

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
