from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator
from .models import Rating
from .models import MenuItem, Category, Rating, Cart
from rest_framework import serializers
from decimal import Decimal
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

################ SIMPLE SERIALIZER #################


# >> While using a simple Serializer calss, you have to manually set every field presnet in the model we have to serialize.
class MenuItemSerializerSimple(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    inventory = serializers.IntegerField()

################ MODEL SERIALIZER ##################


class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


# Adding HyperLinkedModelSerializer to display related models as hyperlinks, but then we have comment out the category field as for now it is for diplaying the realted object
class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    # We are making this write_only because we don;t want to display it on GET requests
    category_id = serializers.IntegerField(write_only=True)

    # >> Relationship serializer: Either we can add a new field and set it to the serializer of the related field. or set depth =1 as a field to display all relations nested in the object

    # 1 >> This will display the category object inside the menu object. Making it read only to avoid errors
    category = CategorySerializer(read_only=True)

    # >> This will only display the string representatin of the related model
    # category = serializers.StringRelatedField()

    # 2 >> depth = 1 : This is more efficient since you don't have to serialize the related data manaulally
    # depth = 1

    # Specifyinf a method as a serializer field
    price_after_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    # changing name of inventory field in the model to stock
    stock = serializers.IntegerField(source='inventory')

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "stock",
                  "price_after_tax", 'category', "category_id"]

        # Data validation
        extra_kwargs = {
            "price": {
                "min_value": 2
            },
            "stock": {"source": "inventory", "min_value": 0},
            # Using UniqueValidator to ensure non dublication of title
            "title": {
                "validators": [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }

        # Using validate function for data validation
        def validate(self, attrs):
            if (attrs['price'] < 2):
                raise serializers.ValidationError(
                    'Price should not be less than 2.0')
            if (attrs['inventory'] < 0):
                raise serializers.ValidationError('Stock cannot be negative')
            return super().validate(attrs)

    def calculate_tax(self, product: MenuItem):
        return product.price * Decimal(1.1)


class RatingSerializer (serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Rating
        fields = ['user', 'menuitem_id', 'rating']

    validators = [
        UniqueTogetherValidator(
            queryset=Rating.objects.all(),
            fields=['user', 'menuitem_id']
        )
    ]

    extra_kwargs = {
        'rating': {'min_value': 0, 'max_value': 5},
    }


# class CartSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         default=serializers.CurrentUserDefault()
#     )

#     menuitem = serializers.PrimaryKeyRelatedField(
#         queryset=MenuItem.objects.all()
#     )

#     unit_price = serializers.DecimalField(
#         max_digits=6,
#         decimal_places=2,
#         read_only=True
#     )

#     # Specifyinf a method as a serializer field
#     # price = serializers.SerializerMethodField(
#     #     method_name="calculate_total_price")

#     class Meta:
#         model = Cart
#         fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

#     def get_unit_price(self, menuitem):
#         # Retrieve the unit price from the related menu item
#         return menuitem.unit_price

#     # def calculate_total_price(self, product: MenuItem,  cart: Cart):
#     #     return Decimal(self.menu_item.price) * cart.quantity

#     def calculate_price(self, validated_data):
#         quantity = validated_data['quantity']
#         unit_price = validated_data['unit_price']
#         return quantity * unit_price

#     def create(self, validated_data):
#         menuitem = validated_data['menuitem']
#         validated_data['unit_price'] = self.get_unit_price(menuitem)
#         validated_data['user'] = self.context['request'].user
#         validated_data['price'] = self.calculate_price(validated_data)
#         return super().create(validated_data)
class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(
        source='menuitem.title', read_only=True)
    menuitem_price = serializers.DecimalField(
        source='menuitem.price', max_digits=6, decimal_places=2, read_only=True)
    menuitem_inventory = serializers.IntegerField(
        source='menuitem.inventory', read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'menuitem', 'menuitem_title', 'menuitem_price',
                  'menuitem_inventory', 'quantity', 'price')
        read_only_fields = ('id', 'user', 'menuitem_title',
                            'menuitem_price', 'menuitem_inventory', 'price')

    def calculate_price(self, validated_data):
        quantity = validated_data['quantity']
        unit_price = validated_data['unit_price']
        return quantity * unit_price

    def create(self, validated_data):
        validated_data['price'] = self.calculate_price(validated_data)
        return super().create(validated_data)
