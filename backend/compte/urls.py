from django.urls import path
from .views import (
    ProfilView, UpdateProfilView, ListeUtilisateursView,
    AttribuerRoleAdminView, ModifierPermissionsAdminView
)

urlpatterns = [
    path('profil/', ProfilView.as_view(), name='profil'),
    path('profil/update/', UpdateProfilView.as_view(), name='update_profil'),
    path('utilisateurs/', ListeUtilisateursView.as_view(), name='liste_utilisateurs'),
    path('admin/attribuer-role/', AttribuerRoleAdminView.as_view(), name='attribuer_role_admin'),
    path('admin/modifier-permissions/<int:id>/', ModifierPermissionsAdminView.as_view(), name='modifier_permissions_admin'),
]
