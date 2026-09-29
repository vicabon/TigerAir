(() => {
  const flights = window.TIGERAIR_DATA.flights;
  const fields = [
    ["country", "抵達國家"], ["origin", "起飛地點"], ["destination", "抵達地點"],
    ["departureTime", "起飛時間"], ["arrivalTime", "抵達時間"], ["operationDateSummary", "適合出發日期"]
  ];
  const labels = { country: "country", origin: "originName", destination: "destinationName" };
  const key = v => v;
  const value = (field, row) => field === "days" ? row.days : row[field];
  const display = (field, val, row) => field === "origin" || field === "destination" ? `${row[field === "origin" ? "originName" : "destinationName"]}（${val}）` : val;
  const filters = document.querySelector("#filters");
  fields.forEach(([field, title]) => {
    const values = [...new Set(flights.flatMap(row => Array.isArray(value(field, row)) ? value(field, row) : [value(field, row)]))].sort((a,b) => String(a).localeCompare(String(b), "zh-Hant", {numeric:true}));
    const box = document.createElement("div"); box.className = "filter";
    const label = document.createElement("label"); label.textContent = `${title}（可複選）`; label.htmlFor = `filter-${field}`;
    const choices = document.createElement("div"); choices.className = "choices"; choices.id = `filter-${field}`; choices.dataset.field = field;
    values.forEach((v, index) => { const item = document.createElement("label"); item.className = "choice"; const input = document.createElement("input"); input.type = "checkbox"; input.value = key(v); input.dataset.field = field; input.id = `filter-${field}-${index}`; input.addEventListener("change", render); const text = document.createElement("span"); text.textContent = display(field, v, flights.find(row => (Array.isArray(value(field,row)) ? value(field,row) : [value(field,row)]).includes(v))); item.append(input, text); choices.append(item); });
    box.append(label, choices); filters.append(box);
  });
  const tbody = document.querySelector("#results");
  function render() {
    const selected = Object.fromEntries(fields.map(([field]) => [field, [...document.querySelectorAll(`input[data-field="${field}"]:checked`)].map(input => input.value)]));
    const result = flights.filter(row => fields.every(([field]) => !selected[field].length || (Array.isArray(value(field,row)) ? value(field,row).some(v => selected[field].includes(String(v))) : selected[field].includes(String(value(field,row))))));
    tbody.innerHTML = result.map(row => `<tr><td>${row.country}</td><td><strong>${row.flightNumber}</strong></td><td class="route">${row.originName}<span class="meta">（${row.origin}）</span></td><td class="route">${row.destinationName}<span class="meta">（${row.destination}）</span></td><td>${row.departureTime}</td><td>${row.arrivalTime}${row.overnight ? "（隔日）" : ""}</td><td>${row.days.join("、")}</td><td>${row.operationDateSummary}</td></tr>`).join("");
    document.querySelector("#count").textContent = `顯示 ${result.length} / ${flights.length} 筆航班`;
  }
  document.querySelector("#clear").addEventListener("click", () => { document.querySelectorAll("input[type=checkbox]").forEach(input => { input.checked = false; }); render(); });
  document.querySelector("#updated").textContent = `資料擷取時間：${window.TIGERAIR_DATA.generatedAt}`;
  render();
})();
