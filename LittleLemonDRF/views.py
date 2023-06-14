from django.shortcuts import render
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# Create your views here.
###################### FUNCTIONS BASED VIRES ####################


@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == "GET":
        # Loading the related models in a single query
        items = MenuItem.objects.select_related('category').all()
        # >> We pass context when we are using HyperlinkedModelSerializer to display related models as serializers
        serialized_item = MenuItemSerializer(
            items, many=True, context={'request': request})
        # return Response(items.values())
        return Response(serialized_item.data)
    if request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)


@api_view()
def single_menu_item(request, id):
    # item = MenuItem.objects.get(pk=id)
    item = get_object_or_404(MenuItem, pk=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)

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
