from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view(), name="menu-items"),
    path('menu-items/<int:id>', views.single_menu_item, name="menu-item-detail"),
    path('category/<int:pk>', views.category_detail, name='category-detail')
]
