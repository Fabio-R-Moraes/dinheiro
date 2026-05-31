from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum, Q, Value
from django.db.models.functions import Coalesce
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

    def get_queryset(self):
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
    
class PartidaUpdateView(UpdateView):
    model = Partida
    form_class = PartidaForm
    template_name = 'partida-form.html'
    success_url = reverse_lazy('contabil:partida-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['lancamento_formset'] = LancamentoFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['lancamento_formset'] = LancamentoFormSet(
                instance=self.object
            )

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lancamento_formset = context['lancamento_formset']

        if lancamento_formset.is_valid():
            self.object = form.save()
            lancamento_formset.instance = self.object
            lancamento_formset.save()
            messages.success(self.request, 'Partida atualizada com sucesso!!!')

            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))
    
class PartidaDeleteView(DeleteView):
    model = Partida
    template_name = 'partida-confirm-delete.html'
    success_url = reverse_lazy('contabil:partida-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Partida excluída com sucesso...')

        return super().delete(request, *args, *kwargs)
    
class PlanoDeContasListView(ListView):
    """
    Listagem pormenorizada do Plano de Contas com slaod por conta e
    saldo acumulado por conta-pai. Todos são calculados em uma única
    passagem pelo banco(sem N+1 queries).
    """
    model = PlanoDeContas
    template_name = 'plano-list.html'
    context_object_name = 'grupos'

    def get_queryset(self):
        return (
            PlanoDeContas.objects.select_related('conta_pai').prefetch_related('subcontas__subcontas').order_by('codigo')
        )
    
    def _saldo_proprio(self, conta, debitos_map, creditos_map):
        d = debitos_map.get(conta.pk, Decimal('0'))
        c = creditos_map.get(conta.pk, Decimal('0'))

        if conta.natureza == 'DEVEDORA':
            return d - c
        
        return c - d
    
    def _saldo_acumulado(self, conta, debitos_map, creditos_map):
        total = self._saldo_proprio(conta, debitos_map, creditos_map)

        for sub in conta.subcontas.all():
            total += self._saldo_acumulado(sub, debitos_map, creditos_map)

        return total
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        debitos_qs = (
            Lancamento.objects.filter(tipo='DEBITO').values('conta_id').annotate(total=Coalesce(Sum('valor'), Value(Decimal('0'))))
        )
        creditos_qs = (
            Lancamento.objects.filter(tipo='CREDITO').values('conta_id').annotate(total=Coalesce(Sum('valor'), Value(Decimal('0'))))
        )
        debitos_map = {r['conta_id']: r['total'] for r in debitos_qs}
        creditos_map = {r['conta_id']: r['total'] for r in creditos_qs}
        raizes = (
            PlanoDeContas.objects.filter(conta_pai=None).prefetch_related('subcontas__subcontas__subcontas').order_by('codigo')
        )
        TIPO_ORDEM = ['ATIVO', 'PASSIVO', 'PATRIMONIO', 'RECEITA', 'DESPESA']
        grupos = []

        for raiz in raizes:
            filhas = sorted(raiz.subcontas.all(), key=lambda c: c.codigo)
            linhas = []

            for filha in filhas:
                netas = sorted(filha.subcontas.all(), key=lambda c: c.codigo)
                sublinhas = []

                for neta in netas:
                    saldo_neta = self._saldo_proprio(neta, debitos_map, creditos_map)
                    sublinhas.append({
                        'conta': neta,
                        'nivel': 3,
                        'saldo': saldo_neta,
                        'saldo_acum': saldo_neta,
                        'tem_filhas': False,
                        'debitos': debitos_map.get(neta.pk, Decimal('0')),
                        'creditos': creditos_map.get(neta.pk, Decimal('0')),
                    })

                saldo_filha_proprio = self._saldo_proprio(filha, debitos_map, creditos_map)
                saldo_filha_acum = self._saldo_acumulado(filha, debitos_map, creditos_map)
                linhas.append({
                    'conta': filha,
                    'nivel': 2,
                    'saldo': saldo_filha_proprio,
                    'saldo_acum': saldo_filha_acum,
                    'tem_filhas': bool(netas),
                    'debitos': debitos_map.get(filha.pk, Decimal('0')),
                    'creditos': creditos_map.get(filha.pk, Decimal('0')),
                    'sublinhas': sublinhas,
                })

            saldo_raiz_proprio =self._saldo_proprio(raiz, debitos_map, creditos_map)
            saldo_raiz_acum = self._saldo_acumulado(raiz, debitos_map, creditos_map)
            grupos.append({
                'conta': raiz,
                'nivel': 1,
                'saldo': saldo_raiz_proprio,
                'saldo_acum': saldo_raiz_acum,
                'linhas': linhas,
                'tipo': raiz.tipo,
            })

        grupos.sort(key=lambda g: TIPO_ORDEM.index(g['tipo']) if g['tipo'] in TIPO_ORDEM else 99)

        def soma_grupos(tipos):
            return sum(g['saldo_acum'] for g in grupos if g['tipo'] in tipos)
        
        total_ativo = soma_grupos(['ATIVO'])
        total_passivo = soma_grupos(['PASSIVO'])
        total_patrimonio = soma_grupos(['PATRIMONIO'])
        total_receitas = soma_grupos(['RECEITA'])
        total_despesas = soma_grupos(['DESPESA'])
        resultado = total_receitas - total_despesas

        context.update({
            'grupos': grupos,
            'total_ativo': total_ativo,
            'total_passivo': total_passivo,
            'total_patrimonio': total_patrimonio,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'resultado': resultado,
        })

        return context
    
class PlanoDeContasCreateView(CreateView):
    model = PlanoDeContas
    form_class = PlanoDeContasForm
    template_name = 'plano-form.html'
    success_url = reverse_lazy('contabil:plano-list')

    def form_valid(self, form):
        messages.success(self.request, 'Conta criada com sucesso!!!')
        return super().form_valid(form)

class PlanoDeContasUpdateView(UpdateView):
    model = PlanoDeContas
    form_class = PlanoDeContasForm
    template_name = 'plano-form.html'
    success_url = reverse_lazy('contabil:plano-list')

    def form_valid(self, form):
        messages.success(self.request, 'Conta atualizada com sucesso!!!')
        return super().form_valid(form)
     
