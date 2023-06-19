from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items/',
         views.menu_items, name="menu-items"),
    path('menu-items/<int:id>', views.single_menu_item, name="menu-item-detail"),
    path('category/<int:pk>', views.category_detail, name='category-detail'),
    path('cart/menu-items/', views.cart),
    path('secret/', views.secret),
    path('api-token-auth', obtain_auth_token),
    path('manager-view/', views.manager_view),
    path('throttle-check', views.throttle_check),
    # path('throttle-check-auth', views.throttle_check_auth)
    path('groups/manager/users', views.managers),

]
