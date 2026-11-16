export const DAY = 86_400_000;

export function parseCsv(csv) {
  // The repository generator writes scalar fields without embedded commas or line breaks.
  const [header, ...lines] = csv.trim().split(/\r?\n/);
  const keys = header.replace(/^\uFEFF/, "").split(",");
  return lines.filter(Boolean).map((line) => {
    const fields = line.split(",");
    if (fields.length !== keys.length) throw new Error("Linha CSV com número incorreto de campos.");
    return Object.fromEntries(keys.map((key, index) => [key, fields[index]]));
  });
}

export function timestamp(value) {
  // Dates in the source have no time zone. UTC arithmetic preserves their nominal clock times.
  return Date.parse(value.replace(" ", "T") + (value.includes(" ") ? ":00Z" : "T00:00:00Z"));
}

export function prepareAdmissions(rows) {
  return rows.map((row) => ({
    unit: row.id_unidade,
    bed: row.id_leito,
    start: timestamp(row.data_entrada),
    end: timestamp(row.data_saida),
    wait: Number(row.tempo_espera_min),
    infection: Number(row.infeccao_hospitalar),
  }));
}

function occupiedTime(admissions, start, end) {
  const beds = new Map();
  for (const admission of admissions) {
    const left = Math.max(start, admission.start);
    const right = Math.min(end, admission.end);
    if (left >= right) continue;
    const intervals = beds.get(admission.bed) ?? [];
    intervals.push([left, right]);
    beds.set(admission.bed, intervals);
  }

  let total = 0;
  for (const intervals of beds.values()) {
    intervals.sort((a, b) => a[0] - b[0]);
    let coveredUntil = start;
    for (const [left, right] of intervals) {
      total += Math.max(0, right - Math.max(left, coveredUntil));
      coveredUntil = Math.max(coveredUntil, right);
    }
  }
  return total;
}

export function summarize(admissions, capacity, start, end) {
  let count = 0;
  let stay = 0;
  let wait = 0;
  let infections = 0;
  for (const admission of admissions) {
    if (admission.start < start || admission.start >= end) continue;
    count++;
    stay += admission.end - admission.start;
    wait += admission.wait;
    infections += admission.infection;
  }
  return {
    count,
    stay: count ? stay / DAY / count : null,
    wait: count ? wait / count : null,
    infection: count ? infections / count : null,
    occupancy: capacity && end > start ? occupiedTime(admissions, start, end) / (capacity * (end - start)) : null,
  };
}

export function monthsBetween(start, end) {
  const first = new Date(start);
  const months = [];
  for (let year = first.getUTCFullYear(), month = first.getUTCMonth(); Date.UTC(year, month) < end; month++) {
    const monthStart = Date.UTC(year, month);
    months.push({
      date: new Date(monthStart),
      start: Math.max(start, monthStart),
      end: Math.min(end, Date.UTC(year, month + 1)),
    });
  }
  return months;
}
