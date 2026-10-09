"""Converte o relatório do Testador de Estratégias do MT4 (.htm) em backtest.js para o video-backtest.html.

Uso: python ferramentas/relatorio_mt4.py Relatorio.htm backtest.js [--cent]
  --cent  conta cent (ProCent): divide valores por 100 para mostrar em dólar.
"""
import html, json, re, sys
from datetime import datetime

NUM = re.compile(r"^-?[\d ]+(?:[.,]\d+)?$")


def numero(s):
    s = s.replace("\xa0", "").replace(" ", "")
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def celulas(linha):
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S | re.I)]


def resumo(texto, nomes):
    """Valor ao lado de um rótulo do resumo (aceita MT4 em português ou inglês)."""
    for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", texto, re.S | re.I):
        c = celulas(linha)
        for i, v in enumerate(c[:-1]):
            if any(v.lower().startswith(n) for n in nomes):
                return c[i + 1]
    return None


def main(entrada, saida, cent):
    bruto = open(entrada, "rb").read()
    texto = bruto.decode("utf-8") if bruto[:3] == b"\xef\xbb\xbf" or b"charset=utf-8" in bruto[:2000].lower() else bruto.decode("cp1252", "replace")
    k = 0.01 if cent else 1.0
    lados, pontos, fechadas = {}, [], []
    for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", texto, re.S | re.I):
        c = celulas(linha)
        if len(c) < 9 or not re.match(r"\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}", c[1]):
            continue
        tipo, ordem = c[2].lower(), c[3]
        if tipo in ("buy", "sell", "compra", "venda"):
            lados[ordem] = "buy" if tipo in ("buy", "compra") else "sell"
        if len(c) < 10:
            continue
        if c[9] and NUM.match(c[9].replace("\xa0", "")):
            ts = int(datetime.strptime(c[1], "%Y.%m.%d %H:%M").timestamp() * 1000)
            saldo = numero(c[9]) * k
            pontos.append([ts, round(saldo, 2)])
            if c[8] and NUM.match(c[8].replace("\xa0", "")):
                fechadas.append({"t": ts, "o": int(ordem) if ordem.isdigit() else ordem, "lado": lados.get(ordem, ""), "vol": numero(c[4]), "lucro": round(numero(c[8]) * k, 2), "saldo": round(saldo, 2)})
    if not pontos:
        sys.exit("Não achei a lista de operações no relatório.")
    dep = resumo(texto, ["depósito inicial", "deposito inicial", "initial deposit"])
    dd = resumo(texto, ["rebaixamento relativo", "relative drawdown"])
    pf = resumo(texto, ["fator de lucro", "profit factor"])
    deposito = numero(dep) * k if dep else round(pontos[0][1] - fechadas[0]["lucro"], 2)
    dd_rel = float(re.search(r"([\d.,]+)%", dd).group(1).replace(",", ".")) if dd and "%" in dd else None
    dados = {"deposito": round(deposito, 2), "final": pontos[-1][1], "dd_rel": dd_rel, "pf": numero(pf) if pf and NUM.match(pf) else None,
             "ops": len(fechadas), "inicio": pontos[0][0], "fim": pontos[-1][0], "pontos": pontos, "fechadas": fechadas}
    open(saida, "w", encoding="utf-8").write("window.LEGATUS_BACKTEST = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"ok: {len(fechadas)} operações, US$ {deposito:,.2f} -> US$ {dados['final']:,.2f}, DD relativo {dd_rel}%, PF {dados['pf']}")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 2:
        sys.exit(__doc__)
    main(a[0], a[1], "--cent" in sys.argv)
