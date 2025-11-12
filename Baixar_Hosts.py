#!/usr/bin/env python3
"""
Baixa várias listas públicas de hosts/domínios, normaliza linhas e gera um arquivo hosts
no formato "0.0.0.0 dominio", removendo duplicatas e ordenando.
"""

import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import sys

# --- CONFIGURAÇÃO ---
LISTAS_URLS = [
    # Coloque aqui as URLs das listas públicas que você quer usar, por exemplo:
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "https://someonewhocares.org/hosts/hosts",
    "https://urlhaus.abuse.ch/downloads/hostfile/",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn/hosts",
    "https://urlhaus.abuse.ch/downloads/hostfile/",
    "http://winhelp2002.mvps.org/hosts.txt",
    "https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt",
    "https://urlhaus.abuse.ch/downloads/hostfile/",
    "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt",
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt"
    ]

SAIDA = "hosts_atualizados.txt"   # arquivo de saída
ALVO_FORM = "0.0.0.0"        # pode usar 0.0.0.0 ou 127.0.0.1
TIMEOUT = 30

# --- FUNÇÕES ---
def baixar_lista(url):
    try:
        print(f"Baixando: {url}")
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return []

def normalizar_linha(linha):
    # Remove comentários e espaços irrelevantes no começo/fim, mas preserva espaço entre IP e host
    s = linha.strip()
    if not s or s.startswith("#"):
        return None
    parts = s.split()
    # Se já estiver no formato "IP dominio ..." mantemos IP+dominio (apenas o primeiro par)
    if len(parts) >= 2 and parts[0].count('.') >= 1 and any(ch.isalpha() for ch in parts[1]):
        ip = parts[0]
        host = parts[1]
        # Normalizamos para ALVO_FORM host (substitui IPs variantes)
        return f"{ALVO_FORM} {host}"
    # Se for apenas "dominio", prefixamos
    if len(parts) == 1 and any(ch.isalpha() for ch in parts[0]):
        return f"{ALVO_FORM} {parts[0]}"
    return None

def main():
    if not LISTAS_URLS:
        print("Adicione URLs em LISTAS_URLS dentro do script antes de rodar.")
        sys.exit(1)

    linhas_todas = []

    # Baixa paralelamente
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(baixar_lista, LISTAS_URLS))

    for bloco in results:
        linhas_todas.extend(bloco)

    # Normaliza e filtra
    normalizadas = []
    for linha in linhas_todas:
        n = normalizar_linha(linha)
        if n:
            normalizadas.append(n)

    # Remove duplicatas preservando UPER/lower? aqui vamos dedup case-insensitive no domínio
    seen = set()
    final = []
    for l in normalizadas:
        # domínio é segunda parte
        try:
            _, dominio = l.split(None, 1)
        except ValueError:
            continue
        chave = dominio.lower()
        if chave not in seen:
            seen.add(chave)
            final.append(f"{ALVO_FORM} {dominio}")

    # Ordena alfabeticamente pelo domínio (case-insensitive)
    final_sorted = sorted(final, key=lambda s: s.split(None,1)[1].lower())

    # Escreve arquivo
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write("# Arquivo gerado: hosts combinados\n")
        f.write("# Formato: IP dominio\n\n")
        for linha in final_sorted:
            f.write(linha + "\n")

    print(f"Pronto — {len(final_sorted)} entradas escritas em {SAIDA}")

if __name__ == "__main__":
    main()
