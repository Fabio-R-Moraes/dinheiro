from django.contrib import admin
from .models import PlanoDeContas, Lancamento, Partida

class LancamentoInline(admin.TabularInline):
    model =Lancamento
    extra = 2
    fields = ['conta', 'tipo', 'valor', 'descricao']

@admin.register(PlanoDeContas)
class PlanoDeContasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'tipo', 'natureza', 'conta_pai', 'ativa']
    list_filter = ['tipo', 'natureza', 'ativa']
    search_fields = ['codigo', 'nome']
    ordering = ['codigo']

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'categoria', 'status', 'valor_total', 'esta_equilibrada']
    list_filter = ['categoria', 'status', 'data']
    search_fields = ['descricao']
    inlines = [LancamentoInline]
    date_hierarchy = 'data'

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ['data', 'conta', 'tipo', 'valor', 'descricao']
    list_filter = ['tipo', 'conta__tipo']
    search_fields = ['descricao', 'conta__nome']
