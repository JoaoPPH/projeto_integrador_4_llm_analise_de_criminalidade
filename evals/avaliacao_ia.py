# Cenário de teste para avaliar as recomendações da IA

cenario = {
    "uf": "ES",
    "municipio": "Vitória",
    "meio_transporte": "Transporte público",
    "acompanhantes": "Crianças",
    "periodo": "Noite",
    "objetivo": "Turismo"
}

# Critérios para avaliar a resposta da IA

criterios = {
    "transporte": "Considera os riscos e cuidados ao usar transporte público",
    "acompanhantes": "Apresenta recomendações adequadas para quem viaja com crianças",
    "periodo": "Considera os cuidados necessários durante a noite",
    "objetivo": "Oferece orientações relacionadas ao turismo"
}

def avaliar_resposta(resposta_ia):
    print("AVALIAÇÃO DA RESPOSTA DA IA")
    print("-" * 40)
    print("Resposta recebida:")
    print(resposta_ia)

    notas = {}

    for nome, descricao in criterios.items():
        print(f"\nCritério: {nome}")
        print(descricao)

        nota = int(input("Digite uma nota de 0 a 2: "))
        notas[nome] = nota

    total = sum(notas.values())

    print("\nRESULTADO DA AVALIAÇÃO")
    print(f"Pontuação total: {total}/8")

if __name__ == "__main__":
    resposta_ia = input("Cole aqui a resposta da IA: ")

    avaliar_resposta(resposta_ia)