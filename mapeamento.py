def criar_mapeamento(deteccoes, confianca_minima=60):

    mapeamento = {}

    for coluna, resultado in deteccoes.items():

        tipo = resultado["tipo"]
        confianca = resultado["confianca"]

        # Ignora detecções muito incertas
        if confianca < confianca_minima:
            continue

        # Se ainda não temos uma coluna desse tipo
        if tipo not in mapeamento:

            mapeamento[tipo] = {
                "coluna": coluna,
                "confianca": confianca
            }

        else:
            # Já existe outra coluna com o mesmo tipo.
            # Mantemos a que tiver maior confiança.

            confianca_atual = mapeamento[tipo]["confianca"]

            if confianca > confianca_atual:

                mapeamento[tipo] = {
                    "coluna": coluna,
                    "confianca": confianca
                }

    return mapeamento