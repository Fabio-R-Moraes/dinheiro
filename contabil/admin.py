from django.contrib import admin
from .models import Conta, Operacao

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ["nome", "criado_em"]
    search_fields = ["nome"]

@admin.register(Operacao)
class OperacaoAdmin(admin.ModelAdmin):
    list_display = ["descricao", "conta", "tipo", "valor", "dataoperacao"]
    list_filter = ["tipo", "conta"]
    search_fields = ["descricao", "conta__nome"]
    date_hierarchy = "dataoperacao"
