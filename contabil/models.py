from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class PlanoDeContas(models.Model):
    #Plano de Contas - Estrutura hierárquica de contas contábeis
    TIPO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('PASSIVO', 'Passivo'),
        ('PATRIMONIO', 'Patrimônio Líquido'),
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    NATUREZA_CHOICES = [
        ('DEVEDORA', 'Devedora'),
        ('CREDORA', 'Credora'),
    ]
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    natureza = models.CharField(max_length=10, choices=NATUREZA_CHOICES)
    conta_pai = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcontas'
    )
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plano de Conta"
        verbose_name_plural = "Plano de Contas"
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nome}'

class Operacao(models.Model):
    TIPO_CHOICES = [
        ("d", "Despesa"),
        ("r", "Receita"),
    ]
    conta = models.ForeignKey(
        Conta, 
        on_delete=models.CASCADE, 
        related_name="operacoes", 
        verbose_name="Conta",
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_CHOICES,
        default="d",
        verbose_name="Tipo",
    )
    valor = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name="Valor"
    )
    dataoperacao = models.DateField(default=timezone.now, verbose_name="Data da Operação")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Operação"
        verbose_name_plural = "Operações"
        ordering = ["-dataoperacao", '-criado_em']

    def __str__(self):
        return f"{self.conta.nome} - {self.descricao}"
