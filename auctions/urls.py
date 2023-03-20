from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing, name='listing'),
    path('bid/<int:listing_id>/', views.bid, name='bid'),
    path('listing/<int:listing_id>/close/', views.close_listing, name='close_listing'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path("categories/", views.categories, name="categories"),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:listing_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('addComment/<int:listing_id>/', views.addComment, name='addComment'),


]
