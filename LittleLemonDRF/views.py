from django.shortcuts import render
from .models import MenuItem, Category, Rating, Cart
from .serializers import MenuItemSerializer, CategorySerializer, RatingSerializer, CartSerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
# Create your views here.
###################### FUNCTIONS BASED VIRES ####################


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        # >> Loading the related models in a single query
        items = MenuItem.objects.select_related('category').all()

        # >> Fetching the query params from the url to implement filtering, searching, ordering and pagination
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        page = request.query_params.get('page', default=1)
        perpage = request.query_params.get('perpage', default=2)

        # >> Loading items on the basis of query_params
        if category_name:
            # Using double underscores in case of related model 'category__title'
            items = items.filter(category__title=category_name)
        elif to_price:
            # __lte is a field lookup. There are man other field lookups but in this case it means lower than equal to
            items = items.filter(price__lte=to_price)

        if search:
            # We can place an 'i' before the '__contains" or "--istartswith" for case sensitivity
            items = items.filter(title__contains=search)

        if ordering:
            # Spliting the ordering value if it contains more than one criteria e.g ordering=price,title
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        # >> Creating a paginator
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except:
            items = []

        # >> We pass context when we are using HyperlinkedModelSerializer to display related models as serializers
        serialized_item = MenuItemSerializer(
            items, many=True, context={'request': request})
        # return Response(items.values())
        return Response(serialized_item.data)

    # >> Checking for POST requests
    if request.method == "POST":
        if request.user.groups.filter(name="Manager").exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)
        else:
            return Response({"message": "You're not autherized"}, 403)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_menu_item(request, id):
    # item = MenuItem.objects.get(pk=id)
    if request.method == "GET":
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)

    if request.method == "PUT":
        if request.user.groups.filter(name="Manager").exists():
            menu_item = get_object_or_404(MenuItem, pk=id)
            serialized_item = MenuItemSerializer(menu_item, data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_200_OK)

        else:
            return Response({"message": "You're not autherized"}, 403)

    if request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists():
            menu_item = get_object_or_404(MenuItem, pk=id)
            menu_item.delete()
            return Response({"message": "Item deleted succesfuly"}, status.HTTP_200_OK)
        else:
            return Response({"message": "You're not autherized"}, 403)

    if request.method == "PATCH":
        if request.user.groups.filter(name="Manager").exists():
            menu_item = get_object_or_404(MenuItem, pk=id)
            serialized_item = MenuItemSerializer(menu_item, data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_200_OK)

        else:
            return Response({"message": "You're not autherized"}, 403)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == "GET":
        cart_items = Cart.objects.select_related('user').all()
        serialized_items = CartSerializer(
            cart_items, many=True)
        # return Response(items.values())
        return Response(serialized_items.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity')
        menuitem = get_object_or_404(MenuItem, pk=menuitem_id)

        if not menuitem_id or not quantity:
            return Response({'error': 'menuitem_id and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update cart item
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'unit_price': menuitem.price,
                'price': int(quantity) * (menuitem.price)
            }
        )

        if not created:
            cart_item.quantity = quantity
            cart_item.price = int(quantity) * menuitem.price
            # cart_item.save()

        serialized_item = CartSerializer(cart_item, data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)

    if request.method == "DELETE":
        cart_items = Cart.objects.select_related('user').all()
        cart_items.delete()
        return Response({"message": "successfully deleted all items"}, status=status.HTTP_200_OK)


# >> Authentication


@api_view()
# This will return response for authenticated users only
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "some secret message"})


@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    # >> We are checking if the user with the token belongs to manager group only, therefore no other token should display this message
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only Manager Should See This"})
    else:
        return Response({"message": "You're not autherized"}, 403)


# >> Throttling
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


# @api_view()
# @permission_classes([IsAuthenticated])
# @throttle_check([UserRateThrottle])
# def throttle_check_auth(request):
#     return Response({"message": "message for the logged in users only"})

# >> User Management
# This view is for super admin to add and remove users from manager groups
@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]

    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")

        if request.method == "POST":
            managers.user_set.add(user)
        elif request.method == "DELETE":
            managers.user_set.remove(user)
        return Response({"message": "ok"})

    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
####################### CLASS BASED VIEWS #####################


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# >>  The least a generic view requires for functioning properly is a serializer_class and queryset


class MenuItemsView(generics.ListCreateAPIView, ):
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price", "inventory"]
    search_fields = ['title', 'category__title']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


# >> The generic view RetrieveUpdateDestroy has everything to create a new model item and delete a model item from the database
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []

        return [IsAuthenticated()]
