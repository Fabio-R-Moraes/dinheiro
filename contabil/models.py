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
    
    def saldo(self):
        debitos = self.lancamentos.filter(tipo='DEBITO').aggregate(
            total=models.Sum('valor')
        )['total'] or Decimal('0')
        creditos = self.lancamentos.filter(tipo='CREDITO').aggregate(
            total=models.Sum('valor')
        )['total'] or Decimal('0')

        if self.natureza == 'DEVEDORA':
            return debitos - creditos
        
        return creditos - debitos

class Lancamento(models.Model):
    #Lançamento contábil - registro de cada partida
    TIPO_CHOICES = [
        ("CREDITO", "Crédito"),
        ("DEBITO", "Débito"),
    ]
    data = models.DateField(default=timezone.now)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    conta = models.ForeignKey(
        PlanoDeContas, on_delete=models.PROTECT, related_name='lancamentos'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    partida = models.ForeignKey(
        'Partida', on_delete=models.CASCADE, related_name='lancamentos'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lançamento"
        verbose_name_plural = "Lançamentos"
        ordering = ['-data']

    def __str__(self):
        return f"{self.data} | {self.conta.nome} | {self.get_tipo_display()} | R$ {self.valor}"
    
class Partida(models.Model):
    #Partida dobrada - agrupa débitos e créditos de uma transação
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO','Cancelado'),
    ]
    CATEGORIA_CHOICES =[
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
        ('TRANSFERENCIA', 'Tranferência'),
    ]
    data = models.DateField(default=timezone.now)
    data_vencimento = models.DateField(null=True, blank=True)
    descricao = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["-data"]

    def __str__(self):
        return f"{self.data} - {self.descricao} ({self.get_categoria_display()})"
    
    def valor_total(self):
        #Retorna o total dos débitos(= total dos créditos numa partida equilibrada)
        return self.lancamentos.filter(tipo='DEBITO').aggregate(
            total=models.Sum('valor')
        )['total'] or Decimal('0')
    
    def esta_equilibrada(self):
        #Verifica se débitos = créditos(Princípio da partida dobrada)
        debitos = self.lancamentos.filter(tipo='DEBITO').aggregate(
                    total=models.Sum('valor')
                )['total'] or Decimal('0')
        creditos = self.lancamentos.filter(tipo='CREDITO').aggregate(
                    total=models.Sum('valor')
                )['total'] or Decimal('0')
        return debitos == creditos
    
    @property
    def valor(self):
        return self.valor_total()

