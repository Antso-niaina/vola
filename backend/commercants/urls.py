from django.urls import path
from .views import (
    GenerateQRCodeView, PaiementQrCodeView,
    HistoriquePaiementsView, HistoriqueRevenusView,
    
    TopCommercantsHeapView, PaiementsParPlageView, ClientsFidelesView,
)

urlpatterns = [
    path('qr-code/generer/', GenerateQRCodeView.as_view(), name='generer_qr_code'),
    path('paiement/', PaiementQrCodeView.as_view(), name='paiement_qr_code'),
    path('historique-paiements/', HistoriquePaiementsView.as_view(), name='historique_paiements'),
    path('historique-revenus/', HistoriqueRevenusView.as_view(), name='historique_revenus'),

    
    path('admin/top-commercants-live/', TopCommercantsHeapView.as_view(), name='top_commercants_heap'),
    path('admin/paiements-plage/', PaiementsParPlageView.as_view(), name='paiements_plage'),
    path('clients-fideles/', ClientsFidelesView.as_view(), name='clients_fideles'),
]
