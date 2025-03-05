from django.core.management.base import BaseCommand
from business_apps.models import PurchaseOrder

class Command(BaseCommand):
    help = 'Ensure all existing orders have unique order_id values with a minimum of 6 digits'

    def handle(self, *args, **options):
        orders = PurchaseOrder.objects.all()
        for order in orders:
            if len(order.id) < 6:
                order.id = order.id.zfill(6)
            order.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated order {order.id}'))
#class Command(BaseCommand):
#    help = 'Generate barcodes for all existing orders'

#    def handle(self, *args, **options):
#        orders = PurchaseOrder.objects.all()
#       for order in orders:
#            if not order.barcode:
#                order.save()
#                self.stdout.write(self.style.SUCCESS(f'Successfully generated barcode for order {order.id}'))
