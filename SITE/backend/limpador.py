import os

def processar_lista_agressiva(arquivo_entrada, arquivo_saida):
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Erro: O arquivo '{arquivo_entrada}' nao foi encontrado.")
        return

    contas_limpas = set()
    print(f"🔍 Analisando {arquivo_entrada}...")

    with open(arquivo_entrada, 'r', encoding='utf-8', errors='ignore') as f:
        for linha in f:
            linha = linha.strip()
            # Se a linha tiver um ':' e não for apenas lixo
            if ':' in linha and len(linha) > 5:
                # Pega a primeira parte e a segunda parte ignorando o resto
                partes = linha.split(':')
                user = partes[0].strip()
                senha = partes[1].strip()
                contas_limpas.add(f"{user}:{senha}")

    with open(arquivo_saida, 'a') as f:
        for conta in contas_limpas:
            f.write(conta + '\n')

    print(f"✅ Sucesso! {len(contas_limpas)} contas formatadas e injetadas.")

if __name__ == "__main__":
    processar_lista_agressiva('sujo.txt', 'database.txt')