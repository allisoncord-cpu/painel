// Portfólio dos copiadores (valor da área do gestor da RoboForex). Atualize aqui: o PC não mexe neste arquivo.
// Para um valor novo: troque valor_usd e data, e acrescente [data, valor] no fim de hist.
window.LEGATUS_PORTFOLIO = {
  valor_usd: 1304.58,
  data: "2026-10-08",
  hist: [["2026-10-05", 552.12], ["2026-10-06", 563.85], ["2026-10-07", 817.71], ["2026-10-08", 1304.58]],
};

// junta com o data.js: vale o valor de data mais recente, e o histórico de cada dia vem deste arquivo
window.legatusPortfolio = function (d) {
  const P = window.LEGATUS_PORTFOLIO;
  if (!d || !P) return d;
  const cc = d.capital_copiadores;
  if (!cc || cc.valor_usd == null || !cc.data || cc.data <= P.data) d.capital_copiadores = { ...(cc || {}), valor_usd: P.valor_usd, data: P.data };
  const m = new Map(d.portfolio_hist || []);
  P.hist.forEach(([dia, v]) => m.set(dia, v));
  d.portfolio_hist = [...m].sort((a, b) => (a[0] < b[0] ? -1 : 1));
  return d;
};
