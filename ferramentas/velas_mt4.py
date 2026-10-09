"""Converte o histórico exportado da Central de Histórico do MT4 (.csv) em velas.js para o video-backtest.html.

Uso: python ferramentas/velas_mt4.py XAUUSD15.csv velas.js [inicio AAAA.MM.DD] [fim AAAA.MM.DD]
Formato do MT4: data,hora,abertura,máxima,mínima,fechamento,volume (ex.: 2025.12.01,01:00,4214.1,4216.0,4210.5,4215.2,123)
"""
import json, sys
from datetime import datetime

def main(entrada, saida, ini=None, fim=None):
    velas = []
    for linha in open(entrada, encoding="utf-8-sig", errors="replace"):
        c = [x.strip() for x in linha.replace(";", ",").split(",")]
        if len(c) < 6 or not c[0][:4].isdigit():
            continue
        dia = c[0].replace("-", ".").replace("/", ".")
        if (ini and dia < ini) or (fim and dia > fim):
            continue
        ts = int(datetime.strptime(dia + " " + c[1][:5], "%Y.%m.%d %H:%M").timestamp() * 1000)
        velas.append([ts] + [round(float(v), 2) for v in c[2:6]])
    velas.sort()
    open(saida, "w").write("window.LEGATUS_VELAS = " + json.dumps(velas, separators=(",", ":")) + ";\n")
    print(f"ok: {len(velas)} velas de {datetime.fromtimestamp(velas[0][0]/1000):%d/%m/%Y} a {datetime.fromtimestamp(velas[-1][0]/1000):%d/%m/%Y}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:5])
