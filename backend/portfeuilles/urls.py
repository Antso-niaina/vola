from django.urls import path
from .views import (
    SoldeView, TransfertArgentView,
    
    TopPortefeuillesView, CyclesSuspectsView,
)

urlpatterns = [
    path('solde/', SoldeView.as_view(), name='solde'),
    path('transfert/', TransfertArgentView.as_view(), name='transfert_argent'),

    
    path('admin/top-portefeuilles/', TopPortefeuillesView.as_view(), name='top_portefeuilles'),
    path('admin/cycles-suspects/', CyclesSuspectsView.as_view(), name='cycles_suspects'),
]
