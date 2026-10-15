from django.urls import path
from .views import (
    TransactionView, DepotAdminAttentView, ValidationDepotView, RefusDepotView,
    RetraitAdminAttentView, ValidationRetraitView, RefusRetraitView,
    DemandeDepotView, DemandeRetraitView,
    
    TopTransactionsView, TransactionsParPlageView,
)

urlpatterns = [
    path('historique/', TransactionView.as_view(), name='historique_transactions'),

    path('demande-depot/', DemandeDepotView.as_view(), name='demande_depot'),
    path('demande-retrait/', DemandeRetraitView.as_view(), name='demande_retrait'),

    path('admin/depots-en-attente/', DepotAdminAttentView.as_view(), name='depots_en_attente'),
    path('admin/valider-depot/<int:id_depot>/', ValidationDepotView.as_view(), name='valider_depot'),
    path('admin/refuser-depot/<int:id_depot>/', RefusDepotView.as_view(), name='refuser_depot'),

    path('admin/retraits-en-attente/', RetraitAdminAttentView.as_view(), name='retraits_en_attente'),
    path('admin/valider-retrait/<int:id_retrait>/', ValidationRetraitView.as_view(), name='valider_retrait'),
    path('admin/refuser-retrait/<int:id_retrait>/', RefusRetraitView.as_view(), name='refuser_retrait'),

    
    path('admin/top-transactions/', TopTransactionsView.as_view(), name='top_transactions'),
    path('admin/plage-montant/', TransactionsParPlageView.as_view(), name='transactions_plage_montant'),
]
