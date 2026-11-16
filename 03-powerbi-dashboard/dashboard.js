import { DAY, monthsBetween, parseCsv, prepareAdmissions, summarize, timestamp } from "./metrics.js";

const find = (id) => document.getElementById(id);
const form = document.querySelector("form");
const startInput = find("start");
const endInput = find("end");
const unitInput = find("unit");
const metricInput = find("metric");
const status = find("status");
const whole = new Intl.NumberFormat("pt-BR");
const decimal = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });
const percent = new Intl.NumberFormat("pt-BR", { style: "percent", maximumFractionDigits: 1 });
const dateFormat = new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" });
const monthFormat = new Intl.DateTimeFormat("pt-BR", { month: "short", year: "2-digit", timeZone: "UTC" });
const metrics = {
  count: { label: "Internações", format: (value) => whole.format(value) },
  occupancy: { label: "Ocupação de leitos", format: (value) => percent.format(value) },
  stay: { label: "Permanência média", format: (value) => decimal.format(value) + " dias" },
  wait: { label: "Espera média", format: (value) => decimal.format(value) + " min" },
  infection: { label: "Taxa de infecção", format: (value) => percent.format(value) },
};
const show = (key, value) => value === null ? "—" : metrics[key].format(value);
const dateInputValue = (value) => new Date(value).toISOString().slice(0, 10);

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

async function csv(name) {
  const response = await fetch(new URL("../dados/" + name, import.meta.url));
  if (!response.ok) throw new Error("Falha ao ler " + name);
  return parseCsv(await response.text());
}

function renderCards(totals) {
  find("cards").replaceChildren(...Object.entries(metrics).map(([key, metric]) => {
    const card = element("div");
    card.append(element("dt", metric.label), element("dd", show(key, totals[key])));
    return card;
  }));
}

function renderUnits(units, start, end) {
  find("units").replaceChildren(...units.map((unit) => {
    const totals = summarize(unit.admissions, unit.capacity, start, end);
    const row = element("tr");
    const heading = element("th", unit.name);
    heading.scope = "row";
    row.append(heading, element("td", whole.format(unit.capacity)));
    for (const key of Object.keys(metrics)) row.append(element("td", show(key, totals[key])));
    return row;
  }));
}

function renderChart(admissions, capacity, start, end) {
  const key = metricInput.value;
  const data = monthsBetween(start, end).map((month) => ({
    label: monthFormat.format(month.date),
    value: summarize(admissions, capacity, month.start, month.end)[key],
  }));
  const max = Math.max(0, ...data.map(({ value }) => value ?? 0));
  find("chart").replaceChildren(...data.map(({ label, value }) => {
    const column = element("div", undefined, "column");
    const track = element("div", undefined, "track");
    track.setAttribute("aria-hidden", "true");
    const bar = element("div", undefined, "bar");
    bar.style.setProperty("--height", (max && value !== null ? value / max * 100 : 0) + "%");
    track.append(bar);
    const valueLabel = element("span", show(key, value));
    valueLabel.title = label + ": " + show(key, value);
    column.append(valueLabel, track, element("span", label, "month"));
    return column;
  }));
  find("scale").textContent = "Escala de 0 a " + show(key, max) + " · — indica ausência de observações.";
}

function setup(unitRows, admissions) {
  const units = unitRows.map((row) => ({
    id: row.id_unidade,
    name: row.nome_unidade,
    capacity: Number(row.capacidade_leitos),
    admissions: admissions.filter((admission) => admission.unit === row.id_unidade),
  }));
  for (const unit of units) unitInput.add(new Option(unit.name, unit.id));
  for (const [key, metric] of Object.entries(metrics)) metricInput.add(new Option(metric.label, key));
  const limits = admissions.map(({ start }) => start);
  const firstDay = dateInputValue(Math.min(...limits));
  const lastDay = dateInputValue(Math.max(...limits));
  for (const [input, initial] of [[startInput, firstDay], [endInput, lastDay]]) {
    input.min = firstDay;
    input.max = lastDay;
    input.defaultValue = initial;
    input.value = initial;
  }

  function render() {
    const start = timestamp(startInput.value);
    const end = timestamp(endInput.value) + DAY;
    const dashboard = find("dashboard");
    if (!form.checkValidity() || end <= start) {
      status.textContent = "Selecione um período válido. A data inicial deve vir antes ou no mesmo dia da data final.";
      dashboard.hidden = true;
      return;
    }
    const selected = units.filter(({ id }) => !unitInput.value || id === unitInput.value);
    const admissions = selected.flatMap((unit) => unit.admissions);
    const capacity = selected.reduce((total, unit) => total + unit.capacity, 0);
    status.textContent = dateFormat.format(start) + " a " + dateFormat.format(end - 1) + " · " +
      (selected.length === 1 ? selected[0].name : selected.length + " unidades");
    renderCards(summarize(admissions, capacity, start, end));
    renderChart(admissions, capacity, start, end);
    renderUnits(selected, start, end);
    dashboard.hidden = false;
  }

  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("change", render);
  form.addEventListener("reset", () => {
    metricInput.selectedIndex = 0;
    queueMicrotask(render);
  });
  metricInput.addEventListener("change", render);
  render();
}

try {
  const [units, admissions] = await Promise.all([csv("unidades.csv"), csv("internacoes.csv")]);
  setup(units, prepareAdmissions(admissions));
} catch (error) {
  status.textContent = "Não foi possível carregar o painel. Inicie o servidor na raiz do repositório e tente novamente.";
  console.error(error);
}
