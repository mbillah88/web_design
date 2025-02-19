from django.db import models

# Create your models here.
from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Received', 'Received'), ('Delivered', 'Delivered')])

    def __str__(self):
        return f"Order {self.id} from {self.supplier.name}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"

class Clients(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class ServiceOrder(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Received', 'Received'), ('Delivered', 'Delivered')])

    def __str__(self):
        return f"ServiceOrder {self.id} from {self.client.name}"
class ServiceOrderItem(models.Model):
    sorder_id = models.ForeignKey(ServiceOrder, related_name='item_sl', on_delete=models.CASCADE, null=True)
    item_id = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)     
    item_qty = models.PositiveBigIntegerField(default=1)
    item_sprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)

    def __str__(self):
        return f"ServiceOrderItem {self.id} for {self.item_id.name} with quantity {self.item_qty}"

class ItemType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ItemSpecification(models.Model):
    spec_name = models.CharField(max_length=100)

    def __str__(self):
        return self.spec_name

class ItemTypeItemSpecification(models.Model):
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    item_specification = models.ForeignKey(ItemSpecification, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item_type.type_name} - {self.item_specification.spec_name}"

class ReceivedItem(models.Model):
    item_name = models.CharField(max_length=100)
    received_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name
        
class ReceivedItemSpec(models.Model):
    received_item = models.ForeignKey(ReceivedItem, on_delete=models.CASCADE)
    item_type_specification = models.ForeignKey(ItemTypeItemSpecification, on_delete=models.CASCADE)
    spec_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.received_item.item_name} - {self.item_type_specification.item_type.type_name} - {self.item_type_specification.item_specification.spec_name}"

class ServicePayment(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"ServicePayment {self.id} for ServiceOrder {self.order.id}"