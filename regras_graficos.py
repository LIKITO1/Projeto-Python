REGRAS_GRAFICOS = {

    "receita_marca": {
        "nome": "Receita por Marca",
        "necessarios": [
            "marca",
            "valor"
        ]
    },

    "participacao_marca": {
        "nome": "Participação das Marcas",
        "necessarios": [
            "marca"
        ]
    },

    "comissao_vendedores": {
        "nome": "Comissão dos Vendedores",
        "necessarios": [
            "vendedor",
            "comissao"
        ]
    },

    "evolucao_vendas": {
        "nome": "Evolução das Vendas",
        "necessarios": [
            "data"
        ]
    },

    "vendas_estado": {
        "nome": "Vendas por Estado",
        "necessarios": [
            "estado"
        ]
    },

    "avaliacoes": {
        "nome": "Avaliações dos Clientes",
        "necessarios": [
            "avaliacao"
        ]
    }
}
def descobrir_graficos_possiveis(mapeamento):

    possiveis = {}

    tipos_disponiveis = set(
        mapeamento.keys()
    )

    for codigo, regra in REGRAS_GRAFICOS.items():

        necessarios = set(
            regra["necessarios"]
        )

        if necessarios.issubset(
            tipos_disponiveis
        ):

            possiveis[codigo] = regra

    return possiveis