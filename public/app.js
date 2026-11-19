let fnChartInstance = null;

function showError(msg) {
  const banner = document.getElementById("error-banner");
  banner.textContent = msg;
  banner.classList.remove("hidden");
}

function clearError() {
  document.getElementById("error-banner").classList.add("hidden");
}

function renderLatex(elementId, latexStr, displayMode = true) {
  const el = document.getElementById(elementId);
  if (window.katex) {
    window.katex.render(latexStr, el, { displayMode, throwOnError: false });
  } else {
    el.textContent = latexStr;
  }
}

async function apiPost(endpoint, payload) {
  clearError();
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Error al procesar el cálculo.");
  }
  return data;
}

function buildGrid(containerId, rows, cols, defaults = null) {
  const container = document.getElementById(containerId);
  container.style.gridTemplateColumns = `repeat(${cols}, 68px)`;
  container.innerHTML = "";
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.value = defaults && defaults[i] && defaults[i][j] !== undefined
        ? defaults[i][j]
        : (i === j ? "1" : "0");
      inp.dataset.r = i;
      inp.dataset.c = j;
      container.appendChild(inp);
    }
  }
}

function readGrid(containerId, rows, cols) {
  const inputs = document.querySelectorAll(`#${containerId} input`);
  const matrix = Array.from({ length: rows }, () => Array(cols).fill("0"));
  inputs.forEach((inp) => {
    matrix[Number(inp.dataset.r)][Number(inp.dataset.c)] = inp.value.trim() || "0";
  });
  return matrix;
}

async function runGaussJordan() {
  const rows = Number(document.getElementById("gj-rows").value);
  const cols = Number(document.getElementById("gj-cols").value);
  const btn = document.getElementById("gj-run");
  btn.disabled = true;
  try {
    const matriz = readGrid("gj-grid", rows, cols);
    const data = await apiPost("/api/gauss-jordan", { matriz });

    renderLatex("gj-orig-latex", data.matriz_original_latex, true);
    renderLatex("gj-rref-latex", data.rref_latex, true);
    document.getElementById("gj-orig-raw").value = data.matriz_original_latex;
    document.getElementById("gj-rref-raw").value = data.rref_latex;

    const nucleoTexto = data.base_nucleo.length
      ? data.base_nucleo.map((v) => `(${v.join(", ")})`).join(" , ")
      : "Trivial { 0 }";

    document.getElementById("gj-meta").innerHTML = `
      <div><strong>Columnas pivote (índice 0):</strong> [${data.columnas_pivote.join(", ")}]</div>
      <div><strong>Intercambios de fila:</strong> ${data.cantidad_intercambios}</div>
      <div><strong>Base del Núcleo (Ker A):</strong> <code>${nucleoTexto}</code></div>
    `;

    const pasosEl = document.getElementById("gj-pasos");
    pasosEl.innerHTML = data.pasos.length
      ? data.pasos.map((p) => `<li>${p}</li>`).join("")
      : "<li>La matriz ya se encuentra en forma escalonada reducida.</li>";

    document.getElementById("gj-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
  }
}

async function runSistema() {
  const rows = Number(document.getElementById("sis-rows").value);
  const cols = Number(document.getElementById("sis-cols").value);
  const btn = document.getElementById("sis-run");
  btn.disabled = true;
  try {
    const matriz_a = readGrid("sis-grid-a", rows, cols);
    const vector_b = readGrid("sis-grid-b", rows, 1).map((r) => r[0]);
    const data = await apiPost("/api/sistema", { matriz_a, vector_b });

    document.getElementById("sis-badge").textContent = data.clasificacion;

    const partStr = data.solucion_particular
      ? `(${data.solucion_particular.join(", ")})`
      : "No existe (Sistema Incompatible)";
    const homStr = data.base_homogeneo.length
      ? data.base_homogeneo.map((v) => `(${v.join(", ")})`).join(" , ")
      : "Trivial { 0 }";

    document.getElementById("sis-solucion").innerHTML = `
      <div><strong>Solución particular xₚ:</strong> <code>${partStr}</code></div>
      <div><strong>Base del homogéneo (Sₕ):</strong> <code>${homStr}</code></div>
    `;

    const pasosEl = document.getElementById("sis-pasos");
    pasosEl.innerHTML = data.pasos.length
      ? data.pasos.map((p) => `<li>${p}</li>`).join("")
      : "<li>No se requirieron operaciones elementales.</li>";

    document.getElementById("sis-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
  }
}

function drawFunctionChart(curvaF, curvaTaylor, criticos) {
  const ctx = document.getElementById("fn-chart").getContext("2d");
  if (fnChartInstance) fnChartInstance.destroy();

  fnChartInstance = new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "f(x)",
          data: curvaF,
          showLine: true,
          borderColor: "#1e3a5f",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
        {
          label: "Polinomio de Taylor Pₙ(x)",
          data: curvaTaylor,
          showLine: true,
          borderColor: "#71717a",
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0.15,
        },
        {
          label: "Puntos críticos",
          data: criticos.map((pc) => ({ x: pc.x, y: pc.y })),
          backgroundColor: "#991b1b",
          pointRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { type: "linear", title: { display: true, text: "x" }, grid: { color: "#f4f4f5" } },
        y: { type: "linear", title: { display: true, text: "y" }, grid: { color: "#f4f4f5" } },
      },
    },
  });
}

async function runFuncion() {
  const btn = document.getElementById("fn-run");
  btn.disabled = true;
  try {
    const payload = {
      expresion: document.getElementById("fn-expr").value.trim(),
      a: Number(document.getElementById("fn-a").value),
      b: Number(document.getElementById("fn-b").value),
      subintervalos: 60,
      taylor_x0: Number(document.getElementById("fn-x0").value),
      taylor_orden: Number(document.getElementById("fn-orden").value),
    };
    const data = await apiPost("/api/estudio-funcion", payload);

    renderLatex("fn-f-latex", data.funcion_latex, false);
    renderLatex("fn-d1-latex", data.derivada_primera_latex, false);
    renderLatex("fn-d2-latex", data.derivada_segunda_latex, false);
    renderLatex("fn-taylor-latex", data.taylor_latex, false);

    document.getElementById("fn-f-raw").value = data.funcion_latex;
    document.getElementById("fn-d1-raw").value = data.derivada_primera_latex;
    document.getElementById("fn-d2-raw").value = data.derivada_segunda_latex;
    document.getElementById("fn-taylor-raw").value = data.taylor_latex;

    const raicesStr = data.raices_aproximadas.length
      ? data.raices_aproximadas.join(", ")
      : "No se detectaron raíces en el intervalo";

    document.getElementById("fn-resumen").innerHTML = `
      <div><strong>Raíces aproximadas:</strong> <code>${raicesStr}</code></div>
      <div><strong>Integral definida (Simpson):</strong> <code>${data.integral_definida}</code></div>
    `;

    const tbody = document.getElementById("fn-criticos");
    tbody.innerHTML = data.puntos_criticos.length
      ? data.puntos_criticos
          .map(
            (pc) => `<tr>
              <td>${pc.x}</td>
              <td>${pc.y}</td>
              <td>${pc.segunda_derivada}</td>
              <td>${pc.clasificacion}</td>
            </tr>`
          )
          .join("")
      : `<tr><td colspan="4">Sin puntos críticos detectados en [a, b].</td></tr>`;

    drawFunctionChart(data.curva_f, data.curva_taylor, data.puntos_criticos);
    document.getElementById("fn-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      clearError();
      document.querySelectorAll(".nav-item").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel-section").forEach((s) => s.classList.add("hidden"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.remove("hidden");
    });
  });

  document.querySelectorAll(".btn-copy").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const val = document.getElementById(btn.dataset.copyTarget).value;
      await navigator.clipboard.writeText(val);
      const orig = btn.textContent;
      btn.textContent = "Copiado";
      setTimeout(() => (btn.textContent = orig), 1200);
    });
  });

  buildGrid("gj-grid", 3, 3, [["1", "2", "-1"], ["2", "4", "1"], ["-1", "-2", "-4"]]);
  buildGrid("sis-grid-a", 3, 3, [["1", "2", "-1"], ["2", "4", "1"], ["-1", "-2", "-4"]]);
  buildGrid("sis-grid-b", 3, 1, [["1"], ["5"], ["-4"]]);

  document.getElementById("gj-resize").addEventListener("click", () => {
    buildGrid("gj-grid", Number(document.getElementById("gj-rows").value), Number(document.getElementById("gj-cols").value));
  });
  document.getElementById("sis-resize").addEventListener("click", () => {
    const r = Number(document.getElementById("sis-rows").value);
    const c = Number(document.getElementById("sis-cols").value);
    buildGrid("sis-grid-a", r, c);
    buildGrid("sis-grid-b", r, 1);
  });

  document.getElementById("gj-run").addEventListener("click", runGaussJordan);
  document.getElementById("sis-run").addEventListener("click", runSistema);
  document.getElementById("fn-run").addEventListener("click", runFuncion);

  fetch("/api/health")
    .then((r) => (r.ok ? "Motor ExactaPy activo" : "Motor no disponible"))
    .then((txt) => (document.getElementById("api-status").textContent = txt))
    .catch(() => (document.getElementById("api-status").textContent = "Sin conexión al backend"));
});