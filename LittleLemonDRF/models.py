from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, default=1)

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users", null=True)
    menuitem_id = models.SmallIntegerField()
    rating_value = models.SmallIntegerField()
    category = models.ForeignKey(User, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # One user can only have one menuitem
    class Meta:
        unique_together = ('menuitem', 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)


class OrderItem(models.Model):
    order = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # one order item will have one menuitem
    class Meta:
        unique_together = ('order', 'menuitem')
