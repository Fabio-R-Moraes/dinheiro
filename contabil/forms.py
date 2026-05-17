from django import forms
from django.forms import inlineformset_factory
from .models import PlanoDeContas, Lancamento, Partida

class PartidaForm(forms.ModelForm):
    class Meta:
        model = Partida
        fields = ['data', 'data_vencimento', 'descricao', 'categoria', 'status', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LancamentoForm(forms.ModelForm):
    class Meta:
        models = Lancamento
        fields = ['conta', 'tipo', 'valor', 'descricao']
        widgets = {
            'conta': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['conta'].queryset = PlanoDeContas.objects.filter(
                ativa=True, subcontas=None
            ).order_by('codigo')

LancamentoFormSet = inlineformset_factory(
    Partida,
    Lancamento,
    form=LancamentoForm,
    extra=2,
    min_num=2,
    validate_min=True,
    can_delete=True,
)

class PlanoDeContasForm(forms.ModelForm):
    class Meta:
        models = PlanoDeContas
        fields = ['codigo', 'nome', 'tipo', 'natureza', 'conta_pai', 'descricao', 'ativa']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'natureza': forms.Select(attrs={'class': 'form-control'}),
            'conta_pai': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }