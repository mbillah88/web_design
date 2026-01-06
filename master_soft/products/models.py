# models.py
from django.db import models
from accounts.models import CustomUser
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid 
from decimal import Decimal, ROUND_HALF_UP

def generate_barcode(product):
    prefix = "BC"
    brand_code = product.brand.code if product.brand and product.brand.code else "GEN"
    category_code = product.category.code if product.category and product.category.code else "CAT"
    model_code = slugify(product.model).upper()[:6] if product.model else "MODEL"

    base = f"{prefix}-{brand_code}-{category_code}-{model_code}"
    count = Product.objects.filter(barcode__startswith=base).count() + 1
    return f"{base}-{str(count).zfill(3)}"
class TransactionType(models.Model):
    MODULE_CHOICES = [
        ("purchase", "পারচেস"),
        ("sales", "সেলস"),
        ("return", "রিটার্ন"),
        ("transfer", "ট্রান্সফার"),
        ("adjustment", "স্টক অ্যাডজাস্ট"),
    ]

    name = models.CharField(max_length=50, help_text="UI label, e.g. 'কম্প্লিট', 'ক্যানসেল'")
    code = models.CharField(max_length=30, help_text="Internal identifier, e.g. 'complete', 'cancel'")
    module = models.CharField(max_length=20, choices=MODULE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("code", "module")
        verbose_name = "Transaction Type"
        verbose_name_plural = "Transaction Types"
        ordering = ["module", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_module_display()})"

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True)  # ✅ Added
    country = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    support_contact = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name).upper()[:6]  # e.g. DELL, HP
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True)  # ✅ Added
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True)
    banner = models.ImageField(upload_to='categories/banners/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name).upper()[:6]  # e.g. LAP, MON
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"
class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. Piece, Box, License
    symbol = models.CharField(max_length=10, blank=True)  # e.g. pcs, bx, lic
    conversion_factor = models.DecimalField(
        max_digits=10, decimal_places=4, default=1.0000,
        help_text="মূল ইউনিটের সাথে রূপান্তর হার (e.g. 1 Box = 12 Piece)"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.name} ({self.symbol})" if self.symbol else self.name

class Warranty(models.Model):
    class WarrantyType(models.TextChoices):
        MANUFACTURER = 'manufacturer', 'প্রস্তুতকারক'
        SELLER = 'seller', 'বিক্রেতা'
        EXTENDED = 'extended', 'বর্ধিত'
        NONE = 'none', 'কোনটি নয়'
        LIFETIME = 'lifetime', 'লাইফটাইম'

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=WarrantyType.choices, default=WarrantyType.MANUFACTURER)

    duration_value = models.PositiveIntegerField(default=0)  # e.g. 3
    duration_unit = models.CharField(max_length=10, choices=[
        ('days', 'দিন'),
        ('months', 'মাস'),
        ('years', 'বছর')
    ], default='months')

    is_lifetime = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    terms = models.TextField(blank=True)

    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def duration_days(self):
        if self.is_lifetime or self.type == self.WarrantyType.LIFETIME:
            return 99999
        if self.duration_unit == 'days':
            return self.duration_value
        elif self.duration_unit == 'months':
            return self.duration_value * 30
        elif self.duration_unit == 'years':
            return self.duration_value * 365
        return 0

    def __str__(self):
        if self.type == self.WarrantyType.NONE:
            return f"{self.name} (কোন ওয়ারেন্টি নেই)"
        if self.is_lifetime or self.type == self.WarrantyType.LIFETIME:
            return f"{self.name} (লাইফটাইম)"
        return f"{self.name} ({self.duration_value} {self.get_duration_unit_display()})"

class Product(models.Model):
    # 🔹 Basic Info
    code = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # 🔹 Classification
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True)

    # 🔹 Pricing & Barcode
    barcode = models.CharField(max_length=50, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock_alert = models.PositiveIntegerField(default=1)    

    # 🔹 Inventory Flags (Tracking only)
    is_serialized = models.BooleanField(default=False, help_text="প্রতিটি ইউনিটের জন্য আলাদা সিরিয়াল ট্র্যাক হবে")
    requires_batch = models.BooleanField(default=False, help_text="ব্যাচ কোড ও মেয়াদ ট্র্যাক করতে হবে")
    is_returnable = models.BooleanField(default=True, help_text="ক্রেতা ফেরত দিতে পারবে")
    is_serviceable = models.BooleanField(default=True, help_text="সার্ভিস/রিপেয়ার ট্র্যাক করা যাবে")

    # 🔹 Lifecycle Defaults
    warranty_duration_months = models.PositiveIntegerField(default=0, help_text="ওয়ারেন্টি মেয়াদ (মাস)")
    service_interval_days = models.PositiveIntegerField(default=0, help_text="পরবর্তী সার্ভিসের সময়কাল (দিন)")

    # 🔹 Status
    is_active = models.BooleanField(default=True)

    # 🔹 Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def generate_code(self):
        prefix = f"{self.brand.code}-{self.category.code}"
        base = f"{prefix}-{slugify(self.model).upper()[:6]}"
        serial = Product.objects.filter(code__startswith=base).count() + 1
        return f"{base}-{str(serial).zfill(3)}"

    def save(self, *args, **kwargs):
        if not self.code and self.brand and self.category and self.model:
            self.code = self.generate_code()

        if not self.barcode:
            self.barcode = generate_barcode(self)

        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.code} - {self.name}"


    class Meta:
        ordering = ['name']
        verbose_name = "Product"
        verbose_name_plural = "Products"

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=50)  # e.g. RAM
    value = models.CharField(max_length=100)  # e.g. 16GB

class ProductSerial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serials')
    serial_number = models.CharField(max_length=100, unique=True)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(blank=True, null=True)
    warranty_days = models.PositiveIntegerField(default=0)
    next_service_due = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def warranty_expiry(self):
        if self.sold_at and self.warranty_days:
            return self.sold_at + timedelta(days=self.warranty_days)
        return None

    def __str__(self):
        return f"{self.serial_number} ({self.product.name})"
class ProductStockLog(models.Model):
    CHANGE_TYPE = (('IN', 'Stock In'), ('OUT', 'Stock Out'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product.name} {self.change_type} {self.quantity} @ {self.timestamp:%Y-%m-%d}"

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150, blank=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    trade_license = models.CharField(max_length=50, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_mobile = models.CharField(max_length=20, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_suppliers')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_suppliers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.company_name})"
class SupplierLedger(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=[("credit", "Credit"), ("debit", "Debit")])
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=150, blank=True)
    customer_type = models.CharField(max_length=50, choices=[('retail', 'Retail'), ('corporate', 'Corporate')], default='retail')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.mobile})"

def get_default_purchase_type():
    obj, _ = TransactionType.objects.get_or_create(
        code="order",
        module="purchase",
        defaults={"name": "অর্ডার"}
    )
    return obj.pk
class Purchase(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("amount", "৳ Amount"),
        ("percent", "% Percent"),
    ]

    supplier = models.ForeignKey("Supplier", on_delete=models.SET_NULL, null=True)
    invoice_no = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default="amount")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    is_returned = models.BooleanField(default=False)

    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.SET_NULL,
        null=True,
        default=get_default_purchase_type,
        limit_choices_to={"module": "purchase"},
        related_name="purchases"
    )

    created_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name='created_purchases')
    updated_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name='updated_purchases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            year = timezone.now().year
            prefix = f"INV-{year}-"
            last = Purchase.objects.filter(invoice_no__startswith=prefix).order_by('id').last()
            last_number = int(last.invoice_no.split('-')[-1]) if last and last.invoice_no else 0
            self.invoice_no = f"{prefix}{str(last_number + 1).zfill(5)}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return sum((item.qty * item.price) for item in self.items.all()) or Decimal("0.00")

    @property
    def net_total(self):
        return max(self.total - self.total_discount, Decimal("0.00"))

    @property
    def due(self):
        return max(self.net_total - self.paid, Decimal("0.00"))

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "❌"
        return f"{self.invoice_no} - {supplier_name}"
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qty = models.PositiveIntegerField(default=1)  # নন-সিরিয়াল প্রোডাক্টের জন্য
    serials = models.ManyToManyField(ProductSerial, related_name='purchase_items', blank=True)

    class Meta:
        ordering = ["purchase", "product"]

    @property
    def quantity(self):
        if self.product.is_serialized:
            return self.serials.count()
        return self.qty

    @property
    def total_price(self):
        return max((self.price * self.quantity) - self.discount, Decimal("0.00"))
    @property
    def subtotal(self):
        return self.total_price

    def clean(self):
        if self.product.is_serialized:
            if self.qty != 0:
                raise ValidationError("Serialized product should not use qty field.")
            for serial in self.serials.all():
                if serial.product != self.product:
                    raise ValidationError(f"Serial {serial.serial_number} does not match product {self.product.name}")
        else:
            if self.serials.exists():
                raise ValidationError("Non-serialized product should not have serials linked.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} [{self.purchase.invoice_no}]"

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    invoice_no = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    is_returned = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_sales')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def due(self):
        return max(self.total - self.paid, 0)
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class Return(models.Model):
    RETURN_TYPE = (('purchase', 'Purchase'), ('sale', 'Sale'))
    type = models.CharField(max_length=10, choices=RETURN_TYPE)
    reference_id = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    date = models.DateField()

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_payment_methods')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_payment_methods')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BasePayment(models.Model):
    method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.CustomUser', related_name="%(class)s_created", on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey('accounts.CustomUser', related_name="%(class)s_updated", on_delete=models.SET_NULL, null=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey('accounts.CustomUser', related_name="%(class)s_deleted", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} ৳{self.amount} → {self.content_object}"

    def soft_delete(self, user):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def get_summary(self):
        return {
            "id": self.id,
            "amount": float(self.amount),
            "method": self.method.name if self.method else None,
            "note": self.note,
            "date": self.date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "type": self.__class__.__name__.replace("Payment", "").lower()
        }

    @classmethod
    def get_model_for_type(cls, payment_type):
        return {
            "purchase": PurchasePayment,
            "sale": SalePayment,
            "expense": ExpensePayment,
            "refund": RefundPayment,
        }.get(payment_type)
        
class PurchasePayment(BasePayment):
    invoice_number = models.CharField(max_length=100, blank=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True)

class SalePayment(BasePayment):
    receipt_number = models.CharField(max_length=100, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True)

class ExpensePayment(BasePayment):
    category = models.ForeignKey('ExpenseType', on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey('accounts.CustomUser', related_name="approved_expenses", on_delete=models.SET_NULL, null=True)

class RefundPayment(BasePayment):
    original_payment = models.ForeignKey(SalePayment, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
class PaymentAudit(models.Model):
    payment_type = models.CharField(max_length=20)
    payment_id = models.PositiveIntegerField()
    action = models.CharField(max_length=20)  # created, updated, deleted
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    changes = models.JSONField()  # Optional: store field diffs

    def __str__(self):
        return f"{self.payment_type} #{self.payment_id} → {self.action}"
class ExpenseType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. "Utility", "Transport"
    code = models.CharField(max_length=50, unique=True)   # e.g. "utility", "transport"
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)         # for dropdown sorting
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name
