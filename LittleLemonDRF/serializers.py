from .models import MenuItem, Category
from rest_framework import serializers
from decimal import Decimal

################ SIMPLE SERIALIZER #################


class MenuItemSerializerSimple(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    inventory = serializers.IntegerField()

################ MODEL SERIALIZER ##################


class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    # >> Relationship serializer.
    # >> This will display the category object inside the menu object
    category = CategorySerializer(read_only=True)

    # >> This will only display the string representatin of the related model
    # category = serializers.StringRelatedField()

    # Specifyinf a method as a serializer field
    price_after_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    # changing name of inventory field in the model to stock
    stock = serializers.IntegerField(source='inventory')

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "stock",
                  "price_after_tax", 'category', "category_id"]

        #
        extra_kwargs = {
            "price": {
                "min_value": 2
            },
            "inventory": {
                "min_value": 0
            }
        }

    def calculate_tax(self, product: MenuItem):
        return product.price * Decimal(1.1)
