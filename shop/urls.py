from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('<int:myid>/', views.detail, name="detail"),
    path('checkout/', views.checkout, name="checkout"),
    path('confirmation/<int:order_id>/', views.confirmation, name="confirmation"),
    path('download_invoice/<int:order_id>/', views.download_invoice, name="download_invoice"),  # Ajoutez cette ligne
    path('about/', views.about, name='about'),
    path('forum/', views.forum, name='forum'),
]