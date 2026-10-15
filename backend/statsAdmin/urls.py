from django.urls import path
from .views import (
    NbrTransactionsView, NbrUtilisateursView, ListeDepotsAttenteView,
    ListeRetraitsAttenteView, TopCommercantsView, TopUtilisateursView,
    TransactionsParPeriodeView,
    
    TransactionsSuspectesView, MetriquesDashboardView, StatsRangeView,
)

urlpatterns = [
    path('nombre-utilisateurs/', NbrUtilisateursView.as_view(), name='nbr_utilisateurs'),
    path('nombre-transactions/', NbrTransactionsView.as_view(), name='nbr_transactions'),
    path('depots-en-attente/', ListeDepotsAttenteView.as_view(), name='stats_depots_attente'),
    path('retraits-en-attente/', ListeRetraitsAttenteView.as_view(), name='stats_retraits_attente'),
    path('top-commercants/', TopCommercantsView.as_view(), name='top_commercants'),
    path('top-utilisateurs/', TopUtilisateursView.as_view(), name='top_utilisateurs'),
    path('transactions-par-periode/', TransactionsParPeriodeView.as_view(), name='transactions_par_periode'),

    
    path('transactions-suspectes/', TransactionsSuspectesView.as_view(), name='transactions_suspectes'),
    path('metriques-dashboard/', MetriquesDashboardView.as_view(), name='metriques_dashboard'),
    path('stats-range/', StatsRangeView.as_view(), name='stats_range'),
]
