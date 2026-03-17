from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listing/', views.listing, name='listing'),
    path('tenders/<int:pk>/', views.tender_detail, name='tender_detail'),
    path('tenders/<int:pk>/delete/', views.delete_tender, name='delete_tender'),
    path('bids/<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('partner/dashboard/', views.dashboard, name='partner_dashboard'),
    path('partner/applications/', views.partner_applications, name='partner_applications'),
    path('contractor/dashboard/', views.contractor_dashboard, name='contractor_dashboard'),
    path('partner/post-tender/', views.post_tender, name='post_tender'),
    path('login/', views.signin, name='login'),
    path('register/', views.signup, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('archive/', views.archive_view, name='archive'),
    path('favorite/toggle/<int:tender_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('bid-format/', views.bid_format_view, name='bid_format'),
    path('regulations/', views.regulations_view, name='regulations'),
]
