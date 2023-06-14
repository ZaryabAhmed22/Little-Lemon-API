from django.shortcuts import render
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# Create your views here.
###################### FUNCTIONS BASED VIRES ####################


def menu_items(request):
    items = MenuItem.objects.all()
    serialized_item = MenuItemSerializer(items, many=True)
    # return Response(items.values())
    return Response(serialized_item.data)


def single_menu_item(request, id):
    # item = MenuItem.objects.get(pk=id)
    item = get_object_or_404(MenuItem, pk=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)


####################### CLASS BASED VIEWS #####################
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# >>  The least a generic view requires for functioning properly is a serializer_class and queryset


class MenuItemsView(generics.ListCreateAPIView):
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price", "inventory"]
    search_fields = ["title"]


# >> The generic view RetrieveUpdateDestroy has everything to create a new model item and delete a model item from the database
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
