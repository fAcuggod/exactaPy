/* ==========================================================================
   ExactaPy — Lógica de interfaz web (UI)
   Consume la API FastAPI existente (/api/health, /api/gauss-jordan,
   /api/sistema, /api/estudio-funcion) sin modificar el motor ni el backend.
   ========================================================================== */

let fnChartInstance = null;

const GJ_EXAMPLES = {
  nucleo: {
    rows: 3,
    cols: 3,
    data: [
      ["1", "2", "-1"],
      ["2", "4", "1"],
      ["-1", "-2", "-4"],
    ],
  },
  fracciones: {
    rows: 3,
    cols: 3,
    data: [
      ["1/2", "1", "-1/3"],
      ["2", "3/2", "1"],
      ["1", "-1/2", "2"],
    ],
  },
  rectangular: {
    rows: 2,
    cols: 4,
    data: [
      ["1", "2", "-1", "3"],
      ["2", "4", "1", "0"],
    ],
  },
};

const SIS_EXAMPLES = {
  sci: {
    rows: 3,
    cols: 3,
    a: [
      ["1", "2", "-1"],
      ["2", "4", "1"],
      ["-1", "-2", "-4"],
    ],
    b: [["1"], ["5"], ["-6"]],
  },
  scd: {
    rows: 3,
    cols: 3,
    a: [
      ["2", "1", "-1"],
      ["-3", "-1", "2"],
      ["-2", "1", "2"],
    ],
    b: [["8"], ["-11"], ["-3"]],
  },
  si: {
    rows: 3,
    cols: 3,
    a: [
      ["1", "1", "1"],
      ["2", "2", "2"],
      ["1", "-1", "0"],
    ],
    b: [["2"], ["5"], ["1"]],
  },
};

const FN_EXAMPLES = {
  cubica: { expr: "x^3 - 3x", a: -3, b: 3, x0: 0, orden: 3 },
  seno: { expr: "sin(x)", a: -3.14, b: 3.14, x0: 0, orden: 5 },
  exponencial: { expr: "e^x - 2x - 1", a: -2, b: 2, x0: 0, orden: 4 },
  logaritmo: { expr: "ln(x) - x + 2", a: 0.2, b: 4, x0: 1, orden: 3 },
};

/* ---------- Utilidades generales ---------- */

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function clampDim(inputId) {
  const inp = document.getElementById(inputId);
  let val = Math.trunc(Number(inp.value));
  if (!Number.isFinite(val) || val < 1) val = 1;
  if (val > 8) val = 8;
  inp.value = String(val);
  return val;
}

function showError(msg) {
  const banner = document.getElementById("error-banner");
  document.getElementById("error-message").textContent = msg;
  banner.classList.remove("hidden");
  banner.scrollIntoView({ block: "nearest" });
}

function clearError() {
  document.getElementById("error-banner").classList.add("hidden");
}

function renderLatex(elementId, latexStr, displayMode = true) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (window.katex) {
    window.katex.render(latexStr, el, { displayMode, throwOnError: false });
  } else {
    el.textContent = latexStr;
  }
}

function fractionToLatex(str) {
  const s = String(str).trim();
  if (!s.includes("/")) return s;
  const [num, den] = s.split("/");
  if (num.startsWith("-")) {
    return `-\\frac{${num.slice(1)}}{${den}}`;
  }
  return `\\frac{${num}}{${den}}`;
}

function vectorToLatex(vec) {
  return `\\begin{pmatrix} ${vec.map(fractionToLatex).join(" \\\\ ")} \\end{pmatrix}`;
}

function subscriptNumber(n) {
  const digits = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
  };
  return String(n)
    .split("")
    .map((ch) => digits[ch] || ch)
    .join("");
}

async function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
}

async function apiPost(endpoint, payload) {
  clearError();
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error("El servidor devolvió una respuesta no válida.");
  }
  if (!res.ok) {
    throw new Error(data.detail || "Error al procesar el cálculo.");
  }
  return data;
}

/* ---------- Construcción y lectura de grillas matriciales ---------- */

function buildMatrixTable(containerId, rows, cols, options = {}) {
  const {
    defaults = null,
    fillMode = "zero",
    colPrefix = "C",
    rowPrefix = "F",
    showRowHeaders = true,
    singleColLabel = null,
  } = options;

  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const table = document.createElement("table");
  table.className = "matrix-table";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  if (showRowHeaders) {
    const corner = document.createElement("th");
    corner.setAttribute("aria-hidden", "true");
    headRow.appendChild(corner);
  }

  for (let j = 0; j < cols; j++) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = singleColLabel || `${colPrefix}${subscriptNumber(j + 1)}`;
    headRow.appendChild(th);
  }
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  for (let i = 0; i < rows; i++) {
    const tr = document.createElement("tr");
    if (showRowHeaders) {
      const th = document.createElement("th");
      th.scope = "row";
      th.className = "row-hdr";
      th.textContent = `${rowPrefix}${rowPrefix.endsWith(".") ? " " : ""}${i + 1}`;
      tr.appendChild(th);
    }

    for (let j = 0; j < cols; j++) {
      const td = document.createElement("td");
      const inp = document.createElement("input");
      inp.type = "text";
      inp.inputMode = "decimal";
      inp.autocomplete = "off";
      inp.spellcheck = false;
      inp.dataset.r = String(i);
      inp.dataset.c = String(j);
      inp.setAttribute(
        "aria-label",
        singleColLabel
          ? `Término independiente fila ${i + 1}`
          : `Fila ${i + 1}, columna ${j + 1}`
      );

      if (defaults && defaults[i] && defaults[i][j] !== undefined) {
        inp.value = defaults[i][j];
      } else if (fillMode === "identity") {
        inp.value = i === j ? "1" : "0";
      } else {
        inp.value = "0";
      }

      td.appendChild(inp);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }

  table.appendChild(tbody);
  container.appendChild(table);
}

function readExistingGrid(containerId) {
  const inputs = document.querySelectorAll(`#${containerId} input`);
  const map = [];
  inputs.forEach((inp) => {
    const r = Number(inp.dataset.r);
    const c = Number(inp.dataset.c);
    if (!map[r]) map[r] = [];
    map[r][c] = inp.value;
  });
  return map;
}

function readGrid(containerId, rows, cols) {
  const inputs = document.querySelectorAll(`#${containerId} input`);
  const matrix = Array.from({ length: rows }, () => Array(cols).fill("0"));
  inputs.forEach((inp) => {
    const r = Number(inp.dataset.r);
    const c = Number(inp.dataset.c);
    if (r < rows && c < cols) {
      matrix[r][c] = inp.value.trim() || "0";
    }
  });
  return matrix;
}

/* ---------- Herramienta 1: Gauss-Jordan y Núcleo ---------- */

function loadGjExample(key) {
  const ex = GJ_EXAMPLES[key];
  if (!ex) return;
  clearError();
  document.getElementById("gj-rows").value = String(ex.rows);
  document.getElementById("gj-cols").value = String(ex.cols);
  buildMatrixTable("gj-grid", ex.rows, ex.cols, {
    defaults: ex.data,
    colPrefix: "C",
    rowPrefix: "F",
  });
}

async function runGaussJordan() {
  const rows = clampDim("gj-rows");
  const cols = clampDim("gj-cols");
  const btn = document.getElementById("gj-run");
  const labelSpan = btn.querySelector("span:last-child");
  const origLabel = labelSpan.textContent;

  btn.disabled = true;
  labelSpan.textContent = "Calculando...";

  try {
    const matriz = readGrid("gj-grid", rows, cols);
    const data = await apiPost("/api/gauss-jordan", { matriz });

    renderLatex("gj-orig-latex", data.matriz_original_latex, true);
    renderLatex("gj-rref-latex", data.rref_latex, true);
    document.getElementById("gj-orig-raw").value = data.matriz_original_latex;
    document.getElementById("gj-rref-raw").value = data.rref_latex;

    const rangoVal = data.columnas_pivote.length;
    const nulidadVal = data.base_nucleo.length;
    const pivotesHuman = data.columnas_pivote.length
      ? data.columnas_pivote.map((c) => `C${subscriptNumber(c + 1)}`).join(", ")
      : "Ninguna";
    const pivotesZero = `[${data.columnas_pivote.join(", ")}]`;

    document.getElementById("gj-metrics").innerHTML = `
      <div class="kv-cell">
        <span class="kv-label">Rango de A</span>
        <span class="kv-value">rg(A) = ${rangoVal}</span>
        <span class="kv-sub">Dimensión de Im(A)</span>
      </div>
      <div class="kv-cell">
        <span class="kv-label">Nulidad</span>
        <span class="kv-value">dim Ker(A) = ${nulidadVal}</span>
        <span class="kv-sub">rg(A) + nul(A) = ${cols}</span>
      </div>
      <div class="kv-cell">
        <span class="kv-label">Columnas pivote</span>
        <span class="kv-value">${escapeHtml(pivotesHuman)}</span>
        <span class="kv-sub">Índice base 0: ${escapeHtml(pivotesZero)}</span>
      </div>
      <div class="kv-cell">
        <span class="kv-label">Intercambios de fila</span>
        <span class="kv-value">${data.cantidad_intercambios}</span>
        <span class="kv-sub">Operaciones Fᵢ ↔ Fⱼ</span>
      </div>
    `;

    let nucleoLatex;
    let nucleoPlain;
    if (data.base_nucleo.length) {
      nucleoLatex = `\\mathcal{B}_{\\ker(A)} = \\left\\{\\, ${data.base_nucleo.map(vectorToLatex).join(",\\; ")} \\,\\right\\}`;
      nucleoPlain = `Vectores generadores: ${data.base_nucleo.map((v) => `(${v.join(", ")})`).join(" , ")}`;
    } else {
      nucleoLatex = `\\ker(A) = \\left\\{\\, \\mathbf{0} \\,\\right\\}`;
      nucleoPlain = "Núcleo trivial { 0 } — las columnas de A son linealmente independientes.";
    }

    renderLatex("gj-nucleo-latex", nucleoLatex, true);
    document.getElementById("gj-nucleo-plain").textContent = nucleoPlain;
    document.getElementById("gj-nucleo-raw").value = nucleoLatex;

    const pasosEl = document.getElementById("gj-pasos");
    document.getElementById("gj-pasos-count").textContent = `(${data.pasos.length} ${data.pasos.length === 1 ? "operación" : "operaciones"})`;
    pasosEl.innerHTML = data.pasos.length
      ? data.pasos.map((p) => `<li>${escapeHtml(p)}</li>`).join("")
      : `<li class="step-empty">La matriz ingresada ya se encuentra en forma escalonada reducida (RREF).</li>`;

    document.getElementById("gj-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
    labelSpan.textContent = origLabel;
  }
}

/* ---------- Herramienta 2: Sistemas Lineales (Ax = b) ---------- */

function loadSisExample(key) {
  const ex = SIS_EXAMPLES[key];
  if (!ex) return;
  clearError();
  document.getElementById("sis-rows").value = String(ex.rows);
  document.getElementById("sis-cols").value = String(ex.cols);
  buildMatrixTable("sis-grid-a", ex.rows, ex.cols, {
    defaults: ex.a,
    colPrefix: "x",
    rowPrefix: "Ec.",
  });
  buildMatrixTable("sis-grid-b", ex.rows, 1, {
    defaults: ex.b,
    showRowHeaders: false,
    singleColLabel: "b",
  });
}

async function runSistema() {
  const rows = clampDim("sis-rows");
  const cols = clampDim("sis-cols");
  const btn = document.getElementById("sis-run");
  const labelSpan = btn.querySelector("span:last-child");
  const origLabel = labelSpan.textContent;

  btn.disabled = true;
  labelSpan.textContent = "Resolviendo...";

  try {
    const matriz_a = readGrid("sis-grid-a", rows, cols);
    const vector_b = readGrid("sis-grid-b", rows, 1).map((r) => r[0]);
    const data = await apiPost("/api/sistema", { matriz_a, vector_b });

    const badge = document.getElementById("sis-badge");
    const desc = document.getElementById("sis-clasificacion-desc");
    badge.textContent = data.clasificacion;
    badge.className = "class-badge";

    if (data.clasificacion.includes("SCD")) {
      badge.classList.add("badge-scd");
      desc.textContent = "El sistema posee una única solución exacta en ℚ.";
    } else if (data.clasificacion.includes("SCI")) {
      badge.classList.add("badge-sci");
      desc.textContent = "El sistema posee infinitas soluciones (conjunto afín S = xₚ + Sₕ).";
    } else {
      badge.classList.add("badge-si");
      desc.textContent = "El sistema es inconsistente y no admite solución (S = ∅).";
    }

    const varsVec = Array.from({ length: cols }, (_, i) => `x_{${i + 1}}`).join(" \\\\ ");
    const inputSystemLatex = `${data.matriz_a_latex} \\begin{pmatrix} ${varsVec} \\end{pmatrix} = ${vectorToLatex(vector_b)}`;
    renderLatex("sis-input-latex", inputSystemLatex, true);
    document.getElementById("sis-input-raw").value = data.matriz_a_latex;

    let solLatex;
    if (!data.solucion_particular) {
      solLatex = "S = \\varnothing";
    } else if (!data.base_homogeneo.length) {
      solLatex = `\\mathbf{x} = ${vectorToLatex(data.solucion_particular)}`;
    } else {
      const terms = data.base_homogeneo.map((v, idx) => {
        const param = data.base_homogeneo.length === 1 ? "\\lambda" : `\\lambda_{${idx + 1}}`;
        return `${param}\\,${vectorToLatex(v)}`;
      });
      const paramsList =
        data.base_homogeneo.length === 1
          ? "\\lambda \\in \\mathbb{Q}"
          : `${data.base_homogeneo.map((_, i) => `\\lambda_{${i + 1}}`).join(", ")} \\in \\mathbb{Q}`;
      solLatex = `\\mathbf{x} = ${vectorToLatex(data.solucion_particular)} + ${terms.join(" + ")}, \\quad ${paramsList}`;
    }

    renderLatex("sis-solucion-latex", solLatex, true);
    document.getElementById("sis-sol-raw").value = solLatex;

    const partStr = data.solucion_particular
      ? `(${data.solucion_particular.join(", ")})`
      : "No existe (Sistema Incompatible)";
    const homStr = data.base_homogeneo.length
      ? data.base_homogeneo.map((v) => `(${v.join(", ")})`).join(" , ")
      : "Trivial { 0 }";

    const coordsRow =
      data.solucion_particular && !data.base_homogeneo.length
        ? `<div class="detail-item">
            <span class="detail-item-label">Valores de las incógnitas:</span>
            <div><code>${escapeHtml(
              data.solucion_particular.map((v, i) => `x${subscriptNumber(i + 1)} = ${v}`).join("  ;  ")
            )}</code></div>
          </div>`
        : "";

    document.getElementById("sis-solucion").innerHTML = `
      ${coordsRow}
      <div class="detail-item">
        <span class="detail-item-label">Solución particular xₚ:</span>
        <div><code>${escapeHtml(partStr)}</code></div>
      </div>
      <div class="detail-item">
        <span class="detail-item-label">Base del sistema homogéneo asociado (Sₕ):</span>
        <div><code>${escapeHtml(homStr)}</code></div>
      </div>
    `;

    const pasosEl = document.getElementById("sis-pasos");
    document.getElementById("sis-pasos-count").textContent = `(${data.pasos.length} ${data.pasos.length === 1 ? "operación" : "operaciones"})`;
    pasosEl.innerHTML = data.pasos.length
      ? data.pasos.map((p) => `<li>${escapeHtml(p)}</li>`).join("")
      : `<li class="step-empty">No se requirieron operaciones elementales adicionales.</li>`;

    document.getElementById("sis-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
    labelSpan.textContent = origLabel;
  }
}

/* ---------- Herramienta 3: Estudio de Función y Taylor ---------- */

function loadFnExample(key) {
  const ex = FN_EXAMPLES[key];
  if (!ex) return;
  clearError();
  document.getElementById("fn-expr").value = ex.expr;
  document.getElementById("fn-a").value = String(ex.a);
  document.getElementById("fn-b").value = String(ex.b);
  document.getElementById("fn-x0").value = String(ex.x0);
  document.getElementById("fn-orden").value = String(ex.orden);
  document.getElementById("fn-expr").focus();
}

function insertAtCursor(input, snippet) {
  const start = input.selectionStart ?? input.value.length;
  const end = input.selectionEnd ?? input.value.length;
  const before = input.value.slice(0, start);
  const after = input.value.slice(end);
  input.value = before + snippet + after;

  let nextPos = start + snippet.length;
  if (snippet === "()") {
    nextPos = start + 1;
  }
  input.focus();
  input.setSelectionRange(nextPos, nextPos);
}

const whiteCanvasPlugin = {
  id: "exactapyWhiteBg",
  beforeDraw(chart) {
    const { ctx, width, height } = chart;
    ctx.save();
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);
    ctx.restore();
  },
};

function drawFunctionChart(curvaF, curvaTaylor, criticos, orden) {
  const ctx = document.getElementById("fn-chart").getContext("2d");
  if (fnChartInstance) fnChartInstance.destroy();

  fnChartInstance = new Chart(ctx, {
    type: "scatter",
    plugins: [whiteCanvasPlugin],
    data: {
      datasets: [
        {
          label: "f(x)",
          data: curvaF,
          showLine: true,
          borderColor: "#157566",
          backgroundColor: "#157566",
          borderWidth: 2.25,
          pointRadius: 0,
          tension: 0.1,
        },
        {
          label: `Polinomio de Taylor P${subscriptNumber(orden)}(x)`,
          data: curvaTaylor,
          showLine: true,
          borderColor: "#121615",
          backgroundColor: "#121615",
          borderWidth: 1.75,
          borderDash: [6, 4],
          pointRadius: 0,
          tension: 0.1,
        },
        {
          label: "Puntos críticos",
          data: criticos.map((pc) => ({ x: pc.x, y: pc.y })),
          backgroundColor: "#b91c1c",
          borderColor: "#ffffff",
          borderWidth: 1.5,
          pointRadius: 5,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          position: "top",
          align: "start",
          labels: {
            color: "#1a1a1a",
            font: { family: '"IBM Plex Sans", sans-serif', size: 12 },
            boxWidth: 18,
            padding: 14,
          },
        },
        tooltip: {
          backgroundColor: "#1a1a1a",
          cornerRadius: 2,
          titleFont: { family: '"IBM Plex Mono", monospace', size: 12 },
          bodyFont: { family: '"IBM Plex Mono", monospace', size: 12 },
        },
      },
      scales: {
        x: {
          type: "linear",
          title: {
            display: true,
            text: "x",
            color: "#1a1a1a",
            font: { family: '"IBM Plex Mono", monospace', size: 13, weight: "600" },
          },
          border: { color: "#444444", width: 1 },
          ticks: {
            color: "#444444",
            font: { family: '"IBM Plex Mono", monospace', size: 11 },
          },
          grid: {
            color: (ctxTick) => (ctxTick.tick && ctxTick.tick.value === 0 ? "#444444" : "#ebebeb"),
            lineWidth: (ctxTick) => (ctxTick.tick && ctxTick.tick.value === 0 ? 1.5 : 1),
          },
        },
        y: {
          type: "linear",
          title: {
            display: true,
            text: "y",
            color: "#1a1a1a",
            font: { family: '"IBM Plex Mono", monospace', size: 13, weight: "600" },
          },
          border: { color: "#444444", width: 1 },
          ticks: {
            color: "#444444",
            font: { family: '"IBM Plex Mono", monospace', size: 11 },
          },
          grid: {
            color: (ctxTick) => (ctxTick.tick && ctxTick.tick.value === 0 ? "#444444" : "#ebebeb"),
            lineWidth: (ctxTick) => (ctxTick.tick && ctxTick.tick.value === 0 ? 1.5 : 1),
          },
        },
      },
    },
  });
}

async function runFuncion() {
  const btnMain = document.getElementById("fn-run");
  const btnInline = document.getElementById("fn-run-inline");
  const mainLabel = btnMain.querySelector("span:last-child");
  const inlineLabel = btnInline.querySelector("span:last-child");
  const origMain = mainLabel.textContent;
  const origInline = inlineLabel.textContent;

  const expresion = document.getElementById("fn-expr").value.trim();
  const a = Number(document.getElementById("fn-a").value);
  const b = Number(document.getElementById("fn-b").value);
  const x0 = Number(document.getElementById("fn-x0").value);
  let orden = Math.trunc(Number(document.getElementById("fn-orden").value));

  if (!expresion) {
    showError("Ingresá una expresión matemática f(x) antes de calcular.");
    return;
  }
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    showError("Los extremos del intervalo [a, b] deben ser números válidos.");
    return;
  }
  if (!Number.isFinite(x0)) {
    showError("El centro de Taylor x₀ debe ser un número válido.");
    return;
  }
  if (!Number.isFinite(orden) || orden < 0) orden = 0;
  if (orden > 10) orden = 10;
  document.getElementById("fn-orden").value = String(orden);

  btnMain.disabled = true;
  btnInline.disabled = true;
  mainLabel.textContent = "Calculando...";
  inlineLabel.textContent = "...";

  try {
    const payload = {
      expresion,
      a,
      b,
      subintervalos: 60,
      taylor_x0: x0,
      taylor_orden: orden,
    };
    const data = await apiPost("/api/estudio-funcion", payload);

    renderLatex("fn-f-latex", data.funcion_latex, false);
    renderLatex("fn-d1-latex", data.derivada_primera_latex, false);
    renderLatex("fn-d2-latex", data.derivada_segunda_latex, false);
    renderLatex("fn-taylor-latex", data.taylor_latex, false);

    document.getElementById("fn-taylor-tag").textContent = `P${subscriptNumber(orden)}(x)`;
    document.getElementById("fn-taylor-desc").textContent = `Taylor de orden ${orden} en x₀ = ${x0}`;
    document.getElementById("fn-chart-title").textContent = `Gráfico comparativo de f(x) y P${subscriptNumber(orden)}(x) en [${a}, ${b}]`;

    document.getElementById("fn-f-raw").value = data.funcion_latex;
    document.getElementById("fn-d1-raw").value = data.derivada_primera_latex;
    document.getElementById("fn-d2-raw").value = data.derivada_segunda_latex;
    document.getElementById("fn-taylor-raw").value = data.taylor_latex;

    const raicesStr = data.raices_aproximadas.length
      ? data.raices_aproximadas.map((r) => `x ≈ ${r}`).join("  ;  ")
      : `No se detectaron raíces en [${a}, ${b}]`;

    document.getElementById("fn-resumen").innerHTML = `
      <div class="detail-item">
        <span class="detail-item-label">Raíces aproximadas (f(x) = 0 en [${escapeHtml(a)}, ${escapeHtml(b)}]):</span>
        <div><code>${escapeHtml(raicesStr)}</code></div>
      </div>
      <div class="detail-item">
        <span class="detail-item-label">Integral definida (Regla de Simpson):</span>
        <div id="fn-integral-latex" class="math-inline"></div>
      </div>
    `;
    renderLatex(
      "fn-integral-latex",
      `\\int_{${a}}^{${b}} f(x)\\,dx \\approx ${data.integral_definida}`,
      false
    );

    const tbody = document.getElementById("fn-criticos");
    tbody.innerHTML = data.puntos_criticos.length
      ? data.puntos_criticos
          .map((pc) => {
            let cls = "extremo-tag";
            if (pc.clasificacion.includes("Mínimo")) cls += " extremo-min";
            else if (pc.clasificacion.includes("Máximo")) cls += " extremo-max";
            return `<tr>
              <td>${escapeHtml(pc.x)}</td>
              <td>${escapeHtml(pc.y)}</td>
              <td>${escapeHtml(pc.segunda_derivada)}</td>
              <td class="cell-text"><span class="${cls}">${escapeHtml(pc.clasificacion)}</span></td>
            </tr>`;
          })
          .join("")
      : `<tr><td colspan="4" class="cell-text">Sin puntos críticos detectados en [${escapeHtml(a)}, ${escapeHtml(b)}].</td></tr>`;

    drawFunctionChart(data.curva_f, data.curva_taylor, data.puntos_criticos, orden);
    document.getElementById("fn-result").classList.remove("hidden");
  } catch (err) {
    showError(err.message);
  } finally {
    btnMain.disabled = false;
    btnInline.disabled = false;
    mainLabel.textContent = origMain;
    inlineLabel.textContent = origInline;
  }
}

/* ---------- Inicialización de eventos ---------- */

document.addEventListener("DOMContentLoaded", () => {
  // Navegación entre herramientas
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      clearError();
      document.querySelectorAll(".nav-item").forEach((b) => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".panel-section").forEach((s) => s.classList.add("hidden"));
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.remove("hidden");
    });
  });

  // Cerrar banner de error
  document.getElementById("error-close").addEventListener("click", clearError);

  // Botones de copiar LaTeX
  document.querySelectorAll(".btn-copy").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = document.getElementById(btn.dataset.copyTarget);
      if (!target || !target.value) return;
      try {
        await copyText(target.value);
        const orig = btn.textContent;
        btn.textContent = "Copiado";
        setTimeout(() => {
          btn.textContent = orig;
        }, 1400);
      } catch {
        showError("No se pudo copiar al portapapeles en este navegador.");
      }
    });
  });

  // Mostrar / ocultar pasos elementales
  document.querySelectorAll("[data-toggle-target]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.dataset.toggleTarget);
      if (!target) return;
      const isHidden = target.classList.toggle("hidden");
      btn.textContent = isHidden ? "Mostrar pasos" : "Ocultar pasos";
    });
  });

  // Estado inicial de grillas con ejemplos útiles
  loadGjExample("nucleo");
  loadSisExample("sci");

  // Ejemplos rápidos: Gauss-Jordan
  document.querySelectorAll("[data-gj-example]").forEach((btn) => {
    btn.addEventListener("click", () => loadGjExample(btn.dataset.gjExample));
  });

  // Controles de grilla: Gauss-Jordan
  const applyGjResize = () => {
    const r = clampDim("gj-rows");
    const c = clampDim("gj-cols");
    const existing = readExistingGrid("gj-grid");
    buildMatrixTable("gj-grid", r, c, {
      defaults: existing,
      fillMode: "zero",
      colPrefix: "C",
      rowPrefix: "F",
    });
  };
  document.getElementById("gj-resize").addEventListener("click", applyGjResize);
  ["gj-rows", "gj-cols"].forEach((id) => {
    document.getElementById(id).addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        applyGjResize();
      }
    });
  });

  document.getElementById("gj-identity").addEventListener("click", () => {
    const r = clampDim("gj-rows");
    const c = clampDim("gj-cols");
    buildMatrixTable("gj-grid", r, c, {
      fillMode: "identity",
      colPrefix: "C",
      rowPrefix: "F",
    });
  });

  document.getElementById("gj-clear").addEventListener("click", () => {
    const r = clampDim("gj-rows");
    const c = clampDim("gj-cols");
    buildMatrixTable("gj-grid", r, c, {
      fillMode: "zero",
      colPrefix: "C",
      rowPrefix: "F",
    });
  });

  // Ejemplos rápidos: Sistemas Lineales
  document.querySelectorAll("[data-sis-example]").forEach((btn) => {
    btn.addEventListener("click", () => loadSisExample(btn.dataset.sisExample));
  });

  // Controles de grilla: Sistemas Lineales
  const applySisResize = () => {
    const r = clampDim("sis-rows");
    const c = clampDim("sis-cols");
    const existingA = readExistingGrid("sis-grid-a");
    const existingB = readExistingGrid("sis-grid-b");
    buildMatrixTable("sis-grid-a", r, c, {
      defaults: existingA,
      fillMode: "zero",
      colPrefix: "x",
      rowPrefix: "Ec.",
    });
    buildMatrixTable("sis-grid-b", r, 1, {
      defaults: existingB,
      fillMode: "zero",
      showRowHeaders: false,
      singleColLabel: "b",
    });
  };
  document.getElementById("sis-resize").addEventListener("click", applySisResize);
  ["sis-rows", "sis-cols"].forEach((id) => {
    document.getElementById(id).addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        applySisResize();
      }
    });
  });

  document.getElementById("sis-clear").addEventListener("click", () => {
    const r = clampDim("sis-rows");
    const c = clampDim("sis-cols");
    buildMatrixTable("sis-grid-a", r, c, {
      fillMode: "zero",
      colPrefix: "x",
      rowPrefix: "Ec.",
    });
    buildMatrixTable("sis-grid-b", r, 1, {
      fillMode: "zero",
      showRowHeaders: false,
      singleColLabel: "b",
    });
  });

  // Ejemplos rápidos: Estudio de Función
  document.querySelectorAll("[data-fn-example]").forEach((btn) => {
    btn.addEventListener("click", () => loadFnExample(btn.dataset.fnExample));
  });

  // Paleta de símbolos matemáticos
  const fnExprInput = document.getElementById("fn-expr");
  document.querySelectorAll(".btn-sym[data-insert]").forEach((btn) => {
    btn.addEventListener("click", () => insertAtCursor(fnExprInput, btn.dataset.insert));
  });
  document.getElementById("fn-clear").addEventListener("click", () => {
    fnExprInput.value = "";
    fnExprInput.focus();
  });

  // Enviar cálculo de función con Enter
  ["fn-expr", "fn-a", "fn-b", "fn-x0", "fn-orden"].forEach((id) => {
    document.getElementById(id).addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        runFuncion();
      }
    });
  });

  // Descargar gráfico PNG
  document.getElementById("fn-download-chart").addEventListener("click", () => {
    if (!fnChartInstance) return;
    const canvas = document.getElementById("fn-chart");
    const link = document.createElement("a");
    link.download = "exactapy-grafico.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  });

  // Botones principales de cálculo
  document.getElementById("gj-run").addEventListener("click", runGaussJordan);
  document.getElementById("sis-run").addEventListener("click", runSistema);
  document.getElementById("fn-run").addEventListener("click", runFuncion);
  document.getElementById("fn-run-inline").addEventListener("click", runFuncion);

  // Estado del motor backend
  const statusEl = document.getElementById("api-status");
  fetch("/api/health")
    .then((r) => {
      if (r.ok) {
        statusEl.textContent = "Motor ExactaPy activo";
        statusEl.className = "status-pill status-ok";
      } else {
        statusEl.textContent = "Motor no disponible";
        statusEl.className = "status-pill status-error";
      }
    })
    .catch(() => {
      statusEl.textContent = "Sin conexión al backend";
      statusEl.className = "status-pill status-error";
    });
});
