from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from datetime import timedelta, date
from decimal import Decimal
from .models import PlanoDeContas, Lancamento, Partida
from .forms import PlanoDeContasForm, LancamentoFormSet, PartidaForm

class HomeView(TemplateView):
    #Dashboard principal com resumo semanal e próximas despesas
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()

        #Semana atual, segunda até domingo
        dia_semana = hoje.weekday() #0 = segunda-feira
        inicio_semana_atual = hoje - timedelta(days=dia_semana)
        fim_semana_atual = inicio_semana_atual + timedelta(days=6)

        #Semana anterior
        inicio_semana_anterior = inicio_semana_atual - timedelta(days=7)
        fim_semana_anterior = inicio_semana_atual - timedelta(days=1)

        #Próximos 4 dias
        proximo_periodo = hoje + timedelta(days=4)

        #Receitas da semana atual
        receitas_atual = Partida.objects.filter(
            categoria='RECEITA',
            data__range=[inicio_semana_atual, fim_semana_atual]
        ).order_by('data')

        #Despesas da semana atual
        despesas_atual = Partida.objects.filter(
            categoria='DESPESA',
            data__range=[inicio_semana_atual, fim_semana_atual]
        ).order_by('data')

        #Receitas da semana anterior
        receitas_anterior = Partida.objects.filter(
            categoria='RECEITA',
            data__range=[inicio_semana_anterior, fim_semana_anterior]
        ).order_by('data')

        #Despesas da semana anterior
        despesas_anterior = Partida.objects.filter(
            categoria='DESPESA',
            data__range=[inicio_semana_anterior, fim_semana_anterior]
        ).order_by('data')

        #Próximas despesas a pagar(Vencimento nos próximos 4 dias - status PENDENTE)
        proximas_despesas = Partida.objects.filter(
            categoria='DESPESA',
            status='PENDENTE',
            data_vencimento__range=[hoje, proximo_periodo]
        ).order_by('data_vencimento')

        #Totais
        def total_partidas(qs):
            total = Decimal('0')

            for p in qs:
                total += p.valor_total()

            return total
        
        context.update({
            'hoje': hoje,
            'inicio_semana_atual': inicio_semana_atual,
            'fim_semana_atual': fim_semana_atual,
            'inicio_semana_anterior': inicio_semana_anterior,
            'fim_semana_anterior': fim_semana_anterior,

            'receitas_atual': receitas_atual,
            'despesas_atual': despesas_atual,
            'total_receitas_atual': total_partidas(receitas_atual),
            'total_despesas_atual': total_partidas(despesas_atual),
            'saldo_atual': total_partidas(receitas_atual) - total_partidas(despesas_atual),

            'receitas_anterior': receitas_anterior,
            'despesas_anterior': despesas_anterior,
             'total_receitas_anterior': total_partidas(receitas_anterior),
            'total_despesas_anterior': total_partidas(despesas_anterior),
            'saldo_anterior': total_partidas(receitas_anterior) - total_partidas(despesas_anterior),

            'proximas_despesas': proximas_despesas,
            'total_proximas_despesas': total_partidas(proximas_despesas),       
            })

        return context
    
class PartidaListView(ListView):
    model = Partida
    template_name = 'partida_list.html'
    context_object_name = 'partidas'
    paginate_by = 20

    def get_ueryset(self):
        qs = Partida.objects.all()
        categoria = self.request.GET.get('categoria')
        status = self.request.GET.get('status')

        if categoria:
            qs = qs.filter(categoria=categoria)

        if status:
            qs = qs.filter(status=status)

        return qs.order_by('-data')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria_atual'] = self.request.GET.get('categoria', '')
        context['status_atual'] = self.request.GET.get('status', '')

        return context
    
class PartidaDetailView(DetailView):
    model = Partida
    template_name = 'partida_detail.html'
    context_object_name = 'partida'

class PartidaCreateView(CreateView):
    model =Partida
    form_class = PartidaForm
    template_name = 'partida-form.html'
    success_url = reverse_lazy('contabil:partida-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['lancamento_formset'] = LancamentoFormSet(self.request.POST)
        else:
            context['lancamento_formset'] = LancamentoFormSet()

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lancamento_formset = context['lancamento_formset']

        if lancamento_formset.is_valid():
            self.object = form.save()
            lancamento_formset.instance = self.object
            lancamento_formset.save()

            if not self.object.esta_equilibrada():
                messages.warning(
                    self.request,
                    'Atenção: a partida não está equilibrada (débitos ≠ créditos)!'
                )
            else:
                messages.success(self.request, 'Partida registrada com sucesso!!!')

            return redirect(self.success_url)
        
        return self.render_to_response(self.get_context_data(form=form))
