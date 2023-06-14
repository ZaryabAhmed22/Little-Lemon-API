from .models import MenuItem, Category
from rest_framework import serializers
from decimal import Decimal

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
