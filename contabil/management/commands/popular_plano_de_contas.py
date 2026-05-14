from django.core.management.base import BaseCommand
from contabil.models import PlanoDeContas


PLANO_INICIAL = [
    # ATIVO
    {'codigo': '1', 'nome': 'ATIVO', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': None},
    {'codigo': '1.1', 'nome': 'Ativo Circulante', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1'},
    {'codigo': '1.1.1', 'nome': 'Caixa', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.1'},
    {'codigo': '1.1.2', 'nome': 'Conta Corrente', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.1'},
    {'codigo': '1.1.3', 'nome': 'Poupança', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.1'},
    {'codigo': '1.1.4', 'nome': 'Carteira Digital (PIX)', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.1'},
    {'codigo': '1.2', 'nome': 'Ativo Não Circulante', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1'},
    {'codigo': '1.2.1', 'nome': 'Veículos', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.2'},
    {'codigo': '1.2.2', 'nome': 'Imóveis', 'tipo': 'ATIVO', 'natureza': 'DEVEDORA', 'pai': '1.2'},

    # PASSIVO
    {'codigo': '2', 'nome': 'PASSIVO', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': None},
    {'codigo': '2.1', 'nome': 'Passivo Circulante', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2'},
    {'codigo': '2.1.1', 'nome': 'Cartão de Crédito', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2.1'},
    {'codigo': '2.1.2', 'nome': 'Empréstimos a Pagar', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2.1'},
    {'codigo': '2.1.3', 'nome': 'Contas a Pagar', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2.1'},
    {'codigo': '2.2', 'nome': 'Passivo Não Circulante', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2'},
    {'codigo': '2.2.1', 'nome': 'Financiamento Imobiliário', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2.2'},
    {'codigo': '2.2.2', 'nome': 'Financiamento de Veículo', 'tipo': 'PASSIVO', 'natureza': 'CREDORA', 'pai': '2.2'},

    # PATRIMÔNIO
    {'codigo': '3', 'nome': 'PATRIMÔNIO LÍQUIDO', 'tipo': 'PATRIMONIO', 'natureza': 'CREDORA', 'pai': None},
    {'codigo': '3.1', 'nome': 'Capital Familiar', 'tipo': 'PATRIMONIO', 'natureza': 'CREDORA', 'pai': '3'},
    {'codigo': '3.2', 'nome': 'Reservas', 'tipo': 'PATRIMONIO', 'natureza': 'CREDORA', 'pai': '3'},

    # RECEITAS
    {'codigo': '4', 'nome': 'RECEITAS', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': None},
    {'codigo': '4.1', 'nome': 'Receitas de Trabalho', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4'},
    {'codigo': '4.1.1', 'nome': 'Salário', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.1'},
    {'codigo': '4.1.2', 'nome': 'Freelance / Bico', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.1'},
    {'codigo': '4.1.3', 'nome': '13º Salário', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.1'},
    {'codigo': '4.1.4', 'nome': 'Férias', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.1'},
    {'codigo': '4.2', 'nome': 'Receitas de Capital', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4'},
    {'codigo': '4.2.1', 'nome': 'Rendimento de Investimentos', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.2'},
    {'codigo': '4.2.2', 'nome': 'Aluguel Recebido', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.2'},
    {'codigo': '4.3', 'nome': 'Outras Receitas', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4'},
    {'codigo': '4.3.1', 'nome': 'Presente / Doação Recebida', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.3'},
    {'codigo': '4.3.2', 'nome': 'Venda de Bens', 'tipo': 'RECEITA', 'natureza': 'CREDORA', 'pai': '4.3'},

    # DESPESAS
    {'codigo': '5', 'nome': 'DESPESAS', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': None},
    {'codigo': '5.1', 'nome': 'Moradia', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.1.1', 'nome': 'Aluguel', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.1'},
    {'codigo': '5.1.2', 'nome': 'Condomínio', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.1'},
    {'codigo': '5.1.3', 'nome': 'Água', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.1'},
    {'codigo': '5.1.4', 'nome': 'Energia Elétrica', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.1'},
    {'codigo': '5.1.5', 'nome': 'Internet / Telefone', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.1'},
    {'codigo': '5.2', 'nome': 'Alimentação', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.2.1', 'nome': 'Supermercado', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.2'},
    {'codigo': '5.2.2', 'nome': 'Restaurante / Delivery', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.2'},
    {'codigo': '5.3', 'nome': 'Transporte', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.3.1', 'nome': 'Combustível', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.3'},
    {'codigo': '5.3.2', 'nome': 'Transporte Público', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.3'},
    {'codigo': '5.3.3', 'nome': 'Aplicativo (Uber/99)', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.3'},
    {'codigo': '5.4', 'nome': 'Saúde', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.4.1', 'nome': 'Plano de Saúde', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.4'},
    {'codigo': '5.4.2', 'nome': 'Medicamentos', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.4'},
    {'codigo': '5.4.3', 'nome': 'Consultas / Exames', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.4'},
    {'codigo': '5.5', 'nome': 'Educação', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.5.1', 'nome': 'Mensalidade Escolar', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.5'},
    {'codigo': '5.5.2', 'nome': 'Cursos e Livros', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.5'},
    {'codigo': '5.6', 'nome': 'Lazer e Entretenimento', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.6.1', 'nome': 'Streaming (Netflix/Spotify)', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.6'},
    {'codigo': '5.6.2', 'nome': 'Passeios e Viagens', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.6'},
    {'codigo': '5.7', 'nome': 'Outras Despesas', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5'},
    {'codigo': '5.7.1', 'nome': 'Vestuário', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.7'},
    {'codigo': '5.7.2', 'nome': 'Impostos e Taxas', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.7'},
    {'codigo': '5.7.3', 'nome': 'Doações / Presentes', 'tipo': 'DESPESA', 'natureza': 'DEVEDORA', 'pai': '5.7'},
]


class Command(BaseCommand):
    help = 'Popula o plano de contas inicial para a família'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando plano de contas...')
        conta_map = {}

        for item in PLANO_INICIAL:
            pai = conta_map.get(item['pai']) if item['pai'] else None
            conta, criada = PlanoDeContas.objects.get_or_create(
                codigo=item['codigo'],
                defaults={
                    'nome': item['nome'],
                    'tipo': item['tipo'],
                    'natureza': item['natureza'],
                    'conta_pai': pai,
                }
            )
            conta_map[item['codigo']] = conta
            status = 'Criada' if criada else 'Já existe'
            self.stdout.write(f'  [{status}] {conta.codigo} - {conta.nome}')

        self.stdout.write(self.style.SUCCESS(
            f'\nPlano de contas configurado com {len(PLANO_INICIAL)} contas!'
        ))