from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conta(models.Model):
    #Tabela de contas financeiras
    nome = models.CharField(max_length=100, verbose_name="Nome da Conta")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )

    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

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
        return f"{self.conta.nome - self.descricao}"
