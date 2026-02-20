from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:product_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/supprimer/<int:item_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('panier/mettre-a-jour/<int:item_id>/', views.mettre_a_jour_panier, name='mettre_a_jour_panier'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),
    path('panier/item/<int:item_id>/ingredients/', views.add_ingredients_to_item, name='add_ingredients_to_item'),
    path('commander/', views.commander, name='commander'),
    path('confirmation/<int:order_id>/', views.confirmation_commande, name='confirmation_commande'),
    path('whatsapp/cart/', views.whatsapp_cart, name='whatsapp_cart'),
    path('whatsapp/commande/<int:order_id>/', views.whatsapp_order, name='whatsapp_order'),
]