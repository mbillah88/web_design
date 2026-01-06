from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# ────────────────────────────────
# 🗂️ Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("ক্যাটাগরি নাম"))
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name=_("বর্ণনা"))

    class Meta:
        verbose_name = _("ক্যাটাগরি")
        verbose_name_plural = _("ক্যাটাগরি তালিকা")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ────────────────────────────────
# 🏷️ Brand Model
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("ব্র্যান্ড নাম"))
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name=_("লোগো"))
    origin_country = models.CharField(max_length=100, blank=True, verbose_name=_("দেশ"))

    class Meta:
        verbose_name = _("ব্র্যান্ড")
        verbose_name_plural = _("ব্র্যান্ড তালিকা")
        ordering = ['name']

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("ইউনিট নাম"))  # যেমন: পিস, বক্স, সেট, কেজি
    symbol = models.CharField(max_length=20, verbose_name=_("প্রতীক"))     # যেমন: pcs, box, set
    description = models.TextField(blank=True, verbose_name=_("বর্ণনা"))
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name=_("মূল ইউনিটের সাথে গুণফল"))
    is_active = models.BooleanField(default=True, verbose_name=_("সক্রিয়"))

    class Meta:
        verbose_name = _("ইউনিট")
        verbose_name_plural = _("ইউনিট তালিকা")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"

# ────────────────────────────────
# 📦 Product Model
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("প্রোডাক্ট নাম"))
    sku = models.CharField(max_length=50, unique=True, verbose_name=_("SKU"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("ক্যাটাগরি"))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("ব্র্যান্ড"))
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, verbose_name=_("ইউনিট"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("মূল্য"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("স্টক"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("ডিসকাউন্ট (%)"))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("প্রোডাক্ট ছবি"))
    description = models.TextField(blank=True, verbose_name=_("বর্ণনা"))
    is_active = models.BooleanField(default=True, verbose_name=_("সক্রিয়"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def final_price(self):
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return f"{self.name} [{self.unit.symbol if self.unit else '—'}]"

    name = models.CharField(max_length=200, verbose_name=_("প্রোডাক্ট নাম"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("ক্যাটাগরি"))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("ব্র্যান্ড"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("মূল্য"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("স্টক"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("ডিসকাউন্ট (%)"))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("প্রোডাক্ট ছবি"))
    description = models.TextField(blank=True, verbose_name=_("বর্ণনা"))
    is_active = models.BooleanField(default=True, verbose_name=_("সক্রিয়"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("তৈরির সময়"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("আপডেট সময়"))

    class Meta:
        verbose_name = _("প্রোডাক্ট")
        verbose_name_plural = _("প্রোডাক্ট তালিকা")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def final_price(self):
        return self.price * (1 - self.discount / 100)

    def stock_status(self):
        if self.stock == 0:
            return _("স্টক শেষ")
        elif self.stock < 5:
            return _("কম স্টক")
        return _("উপলব্ধ")

    def image_preview(self):
        if self.image:
            return f'<img src="{self.image.url}" width="60"/>'
        return _("ছবি নেই")
    image_preview.allow_tags = True
    image_preview.short_description = _("প্রিভিউ")

