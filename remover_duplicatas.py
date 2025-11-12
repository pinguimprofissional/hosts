# Nome do arquivo de entrada e saída
arquivo_entrada = "hosts_atualizados.txt"
arquivo_saida = "HostBloqueados.txt"

# Lê todas as linhas do arquivo
with open(arquivo_entrada, "r", encoding="utf-8") as f:
    linhas = f.readlines()

# Remove quebras de linha, mas mantém os espaços internos e no início/fim
linhas_limpa = [linha.rstrip('\n\r') for linha in linhas]

# Remove duplicatas exatas, preservando o conteúdo original e a ordem alfabética
linhas_unicas = sorted(set(linhas_limpa), key=str.lower)

# Escreve o resultado em outro arquivo
with open(arquivo_saida, "w", encoding="utf-8") as f:
    for linha in linhas_unicas:
        f.write(linha + "\n")

print(f"✅ {len(linhas_unicas)} linhas únicas gravadas em '{arquivo_saida}'.")