from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    InscriptionView, ConnexionView, VerifierOTPView,
    DeconnexionView, ChangerMotDePasseView,
    ListeUtilisateursView, AttribuerRoleAdminView, ModifierPermissionsAdminView
)

urlpatterns = [
    path('inscription/', InscriptionView.as_view(), name='inscription'),
    path('connexion/', ConnexionView.as_view(), name='connexion'),
    path('verifier-otp/', VerifierOTPView.as_view(), name='verifier_otp'),
    path('deconnexion/', DeconnexionView.as_view(), name='deconnexion'),
    path('changer-mot-de-passe/', ChangerMotDePasseView.as_view(), name='changer_mot_de_passe'),
    path('utilisateurs/', ListeUtilisateursView.as_view(), name='liste_utilisateurs'),
    path('attribuer-admin/', AttribuerRoleAdminView.as_view(), name='attribuer_role_admin'),
    path('modifier-permissions-admin/', ModifierPermissionsAdminView.as_view(), name='modifier_permissions_admin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
