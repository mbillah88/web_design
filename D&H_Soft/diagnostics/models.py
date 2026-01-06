from django.db import models
from accounts.models import CustomUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
import uuid


# Hospital and Diagnostic Center Models 
class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    patient_code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    age = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.patient_code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.patient_code:
            today = timezone.localtime().date()
            prefix = f"PID{today.strftime('%y%m%d')}"  # e.g. PID251121
            last_patient = Patient.objects.filter(patient_code__startswith=prefix).order_by('id').last()
            if last_patient and last_patient.patient_code:
                last_number = int(last_patient.patient_code[-4:])
                next_number = last_number + 1
            else:
                next_number = 1
            self.patient_code = f"{prefix}{next_number:04d}"  # e.g. PID2511210001
        super().save(*args, **kwargs)
class Consultant(models.Model):
    CONSULTANT_TYPE_CHOICES = [
        ('internal', 'Internal Consultant'),
        ('external', 'External Consultant'),
        ('referrer', 'Referrer'),
    ]

    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=CONSULTANT_TYPE_CHOICES)
    specialization = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_type_display()})"

    def clean(self):
        if not self.type:
            raise ValidationError("Consultant type is required to generate code.")

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.code:
            today = timezone.localtime().date()
            date_part = today.strftime('%y%m%d')

            prefix_map = {
                'internal': 'INT',
                'external': 'EXT',
                'referrer': 'REF',
            }
            prefix = prefix_map.get(self.type, 'CNS')  # fallback

            base_prefix = f"{prefix}{date_part}"

            last = Consultant.objects.filter(code__startswith=base_prefix).order_by('id').last()
            if last and last.code:
                try:
                    last_number = int(last.code[-4:])
                except ValueError:
                    last_number = 0
                next_number = last_number + 1
            else:
                next_number = 1

            self.code = f"{base_prefix}{next_number:04d}"  # e.g. INT2511280001

        super().save(*args, **kwargs)

# Test Management Models
class TestCategory(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)    
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            today = timezone.localtime().date()
            prefix = f"CAT{today.strftime('%y')}"
            last = TestCategory.objects.filter(code__startswith=prefix).order_by('id').last()
            next_number = int(last.code[-4:]) + 1 if last and last.code else 1
            self.code = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)
class TestSubCategory(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.code:
            today = timezone.localtime().date()
            prefix = f"SUB{today.strftime('%y')}"
            last = TestSubCategory.objects.filter(code__startswith=prefix).order_by('id').last()
            next_number = int(last.code[-4:]) + 1 if last and last.code else 1
            self.code = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)
class TestGroup(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    sub_category = models.ForeignKey(TestSubCategory, on_delete=models.CASCADE) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percent_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    update_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_effective_price(self):
        if self.discounted_price:
            return self.discounted_price
        elif self.percent_discount:
            return self.price - (self.price * self.percent_discount / 100)
        return self.price

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = "TG-"
            for i in range(1, 10000):  # সর্বোচ্চ TG-9999 পর্যন্ত
                candidate_code = f"{prefix}{i:04d}"
                if not TestGroup.objects.filter(code=candidate_code).exists():
                    self.code = candidate_code
                    break
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            raise IntegrityError("Duplicate code generated. Please try again.")

class TestItem(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    group = models.ForeignKey(TestGroup, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, blank=True)
    unit2 = models.CharField(max_length=20, blank=True)
    math = models.CharField(max_length=50, blank=True)
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.group.name})"

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = "T-"
            last = TestItem.objects.filter(code__startswith=prefix).order_by('id').last()
            if last and last.code:
                try:
                    last_number = int(last.code.replace(prefix, ""))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            next_number = last_number + 1
            self.code = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)

class TestGroupItem(models.Model):
    group = models.ForeignKey(TestGroup, on_delete=models.CASCADE, related_name='group_items')
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE, related_name='group_links')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('group', 'item')
        ordering = ['group', 'order']

    def __str__(self):
        return f"{self.group.code} → {self.item.code} (#{self.order})"

class TestAccessory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.name} - ৳{self.price}"   
        
# Hospital..........:
class BedType(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g. 'general', 'cabin', 'icu'
    name = models.CharField(max_length=50)               # e.g. 'General', 'Cabin', 'ICU'
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (৳{self.daily_rate}/day)"
class Bed(models.Model):
    name = models.CharField(max_length=50)  # e.g. "Bed-101", "Cabin-3A"
    bed_type = models.ForeignKey('BedType', on_delete=models.PROTECT)
    is_occupied = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('available','Available'),('occupied','Occupied'),('cleaning','Cleaning'),('reserved','Reserved')], default='available')
    
    def __str__(self):
        return f"{self.name} [{self.bed_type.name}]"

    @property
    def daily_rate(self):
        return self.bed_type.daily_rate

class IPDAdmission(models.Model):
    visit = models.OneToOneField('PatientVisit', on_delete=models.CASCADE)

    admission_code = models.CharField(max_length=20, unique=True, editable=False, blank=True, null=True)

    admission_date = models.DateTimeField(auto_now_add=True)
    discharge_date = models.DateTimeField(null=True, blank=True)

    current_bed = models.ForeignKey('Bed', on_delete=models.SET_NULL, null=True, blank=True)
    current_consultant = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True)

    admission_reason = models.TextField(blank=True)
    is_discharged = models.BooleanField(default=False)
    discharge_summary = models.TextField(blank=True)

    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')
    
    cancelled_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='ipd_admission_cancelled_by')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)    

    def __str__(self):
        return f"{self.admission_code} – {self.visit.patient.name}"

    
    def save(self, *args, **kwargs):
        if not self.admission_code:
            self.admission_code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        prefix = "ADM"
        today = timezone.now().date()
        date_part = today.strftime("%y%m%d")

        # Count existing admissions for today
        count_today = IPDAdmission.objects.filter(
            admission_date__date=today
        ).count() + 1

        serial = str(count_today).zfill(4)  # e.g. 0001, 0002
        return f"{prefix}-{date_part}-{serial}"

class BedTransferLog(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='bed_transfers')
    from_bed = models.ForeignKey('Bed', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    to_bed = models.ForeignKey('Bed', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    transfer_time = models.DateTimeField(auto_now_add=True)
    transferred_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.from_bed} → {self.to_bed} at {self.transfer_time}"
class ConsultantChangeLog(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='consultant_changes')
    from_consultant = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    to_consultant = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    change_time = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.from_consultant} → {self.to_consultant} at {self.change_time}"

class BedChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='bed_charges')
    bed = models.ForeignKey('Bed', on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_days = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.bed} | {self.total_days} days | ৳{self.total_amount}"
class OTChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='ot_charges')
    procedure_name = models.CharField(max_length=100)
    ot_room = models.CharField(max_length=50)
    performed_on = models.DateTimeField()
    surgeon = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True)
    charge = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.procedure_name} - ৳{self.charge}"
class MedicineChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='medicine_charges')
    medicine_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.medicine_name} x{self.quantity} = ৳{self.total_price}"
class ConsultationChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='consultation_charges')
    consultant = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True)
    visit_date = models.DateField()
    charge = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.consultant} on {self.visit_date} - ৳{self.charge}"
class NursingChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='nursing_charges')
    shift = models.CharField(max_length=50)  # e.g., "Day", "Night"
    date = models.DateField()
    charge = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Nursing ({self.shift}) - {self.date} - ৳{self.charge}"
class PackageChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='package_charges')
    package_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    charge = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.package_name} - ৳{self.charge}"
class MiscChargeEntry(models.Model):
    admission = models.ForeignKey('IPDAdmission', on_delete=models.CASCADE, related_name='misc_charges')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    charge = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} - ৳{self.charge}"

class IPDInvoice(models.Model):
    invoice_code = models.CharField(max_length=20, unique=True, blank=True)
    admission = models.OneToOneField('IPDAdmission', on_delete=models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    visit = models.ForeignKey('PatientVisit', on_delete=models.CASCADE)

    advice_entries = models.ManyToManyField('AdviceEntry', related_name='ipd_invoices')
    bed_charge_entries = models.ManyToManyField('BedChargeEntry', blank=True, related_name='invoices')
    ot_charge_entries = models.ManyToManyField('OTChargeEntry', blank=True, related_name='invoices')
    medicine_charge_entries = models.ManyToManyField('MedicineChargeEntry', blank=True, related_name='invoices')
    nursing_charge_entries = models.ManyToManyField('NursingChargeEntry', blank=True, related_name='invoices')
    consultation_charge_entries = models.ManyToManyField('ConsultationChargeEntry', blank=True, related_name='invoices')
    package_charge_entries = models.ManyToManyField('PackageChargeEntry', blank=True, related_name='invoices')
    misc_charge_entries = models.ManyToManyField('MiscChargeEntry', blank=True, related_name='invoices')

    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_code:
            today = timezone.localtime().date()
            prefix = f"IINV{today.strftime('%y%m%d')}"
            last = IPDInvoice.objects.filter(invoice_code__startswith=prefix).order_by('id').last()
            num = int(last.invoice_code[-4:]) if last else 0
            self.invoice_code = f"{prefix}{num + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"IPDInvoice {self.invoice_code}"

    @property
    def total_discount(self):
        return sum(a.discount_amount for a in self.advice_entries.all()) + self.discount

    @property
    def payments(self):
        from django.contrib.contenttypes.models import ContentType
        return Payment.objects.filter(
            invoice_type=ContentType.objects.get_for_model(self.__class__),
            invoice_id=self.id,
            is_cancelled=False
        )

    @property
    def total_paid(self):
        return sum(p.total_amount for p in self.payments)

    @property
    def is_fully_paid(self):
        return self.total_paid >= self.net_amount

    @property
    def get_total_particulars(self):
        return (
            sum(a.final_price for a in self.advice_entries.all()) +
            sum(b.total_amount for b in self.bed_charge_entries.all()) +
            sum(o.charge for o in self.ot_charge_entries.all()) +
            sum(m.total_price for m in self.medicine_charge_entries.all()) +
            sum(n.charge for n in self.nursing_charge_entries.all()) +
            sum(c.charge for c in self.consultation_charge_entries.all()) +
            sum(p.charge for p in self.package_charge_entries.all()) +
            sum(x.charge for x in self.misc_charge_entries.all())
        )

class AdviceInvoice(models.Model):
    invoice_code = models.CharField(max_length=20, unique=True, blank=True)
    visit = models.ForeignKey('PatientVisit', on_delete=models.CASCADE)
    visit_code = models.CharField(max_length=30)  # soft link
    admission = models.ForeignKey('IPDAdmission', on_delete=models.SET_NULL, null=True, blank=True)

    advice_entries = models.ManyToManyField('AdviceEntry', related_name='advice_invoices')
    accessory_entries = models.ManyToManyField('TestAccessoryEntry', related_name='accessory_invoices', blank=True)

    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accessory_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.invoice_code:
            today = timezone.localtime().date()
            prefix = f"AINV{today.strftime('%y%m%d')}"
            last = AdviceInvoice.objects.filter(invoice_code__startswith=prefix).order_by('id').last()
            num = int(last.invoice_code[-4:]) if last else 0
            self.invoice_code = f"{prefix}{num + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"AdviceInvoice {self.invoice_code}"

    @property
    def total_discount(self):
        return sum(a.discount_amount for a in self.advice_entries.all()) + self.discount

    @property
    def payments(self):
        from django.contrib.contenttypes.models import ContentType
        return Payment.objects.filter(
            invoice_type=ContentType.objects.get_for_model(self.__class__),
            invoice_id=self.id,
            is_cancelled=False
        )

    @property
    def total_paid(self):
        return sum(p.total_amount for p in self.payments)

    @property
    def is_fully_paid(self):
        return self.total_paid >= self.net_amount

# Diagnostic Center.........
class PatientVisit(models.Model):
    VISIT_TYPE_CHOICES = [
        ('OPD', 'OPD Visit'),
        ('IPD', 'IPD Admission'),
    ]

    visit_code = models.CharField(max_length=30, unique=True, blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    visit_type = models.CharField(max_length=10, choices=VISIT_TYPE_CHOICES)
    visit_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    consultant = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True, related_name='advised_visits')
    referred_by = models.ForeignKey('Consultant', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_visits')

    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visit_code} ({self.get_visit_type_display()})"

    def save(self, *args, **kwargs):
        if not self.visit_code:
            today = timezone.localtime().date()
            prefix = f"VST{today.strftime('%y%m%d')}"
            last_visit = PatientVisit.objects.filter(visit_code__startswith=prefix).order_by('id').last()
            try:
                last_number = int(last_visit.visit_code[-4:]) if last_visit and last_visit.visit_code else 0
            except ValueError:
                last_number = 0
            self.visit_code = f"{prefix}{last_number + 1:04d}"
        super().save(*args, **kwargs)

    def get_commission_source(self):
        return self.referred_by

class AdviceEntry(models.Model):
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE)
    visit_code = models.CharField(max_length=30)  # soft link
    group = models.ForeignKey(TestGroup, on_delete=models.CASCADE)
    advised_by = models.ForeignKey(Consultant, on_delete=models.SET_NULL, null=True, blank=True)
    advised_at = models.DateTimeField(default=timezone.now)

    price_at_entry = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_billed = models.BooleanField(default=False)
    is_commission_paid = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(default='', blank=True)
    cancelled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_advice_entries')
    cancelled_at = models.DateTimeField(null=True, blank=True)

    advice_invoice = models.ForeignKey(AdviceInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    ipd_invoice = models.ForeignKey(IPDInvoice, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_advice_entries')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_advice_entries')

    def __str__(self):
        return f"{self.group.name} for {self.visit.patient.name}"

    class Meta:
        db_table = 'diagnostics_adviceentry'
        ordering = ['-advised_at']
class TestAccessoryEntry(models.Model):
    visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE)
    visit_code = models.CharField(max_length=30)  # soft link
    accessory = models.ForeignKey(TestAccessory, on_delete=models.CASCADE)
    
    price_at_entry = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(default='', blank=True)
    cancelled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_accessory_entries')
    cancelled_at = models.DateTimeField(null=True, blank=True)

    accessory_invoice = models.ForeignKey(AdviceInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    ipd_invoice = models.ForeignKey(IPDInvoice, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_accessory_entries')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_accessory_entries')

    def __str__(self):
        return f"{self.accessory.name} for {self.visit.patient.name}"

    class Meta:
        db_table = 'diagnostics_testaccessoryentry'

class TestResult(models.Model):
    visit = models.ForeignKey(
        'PatientVisit',
        on_delete=models.CASCADE,
        related_name='results',
        db_index=True
    )
    advice_entry = models.ForeignKey(
        'AdviceEntry',
        on_delete=models.CASCADE,
        related_name='results',
        db_index=True
    )
    test_item = models.ForeignKey(
        'TestItem',
        on_delete=models.CASCADE,
        db_index=True
    )

    # ✅ Machine result (auto-imported)
    machine_result = models.CharField(max_length=100, blank=True, null=True)
    machine_unit = models.CharField(max_length=20, blank=True, null=True)
    machine_reported_at = models.DateTimeField(blank=True, null=True)

    # ✅ Manual override (editable)
    edited_result = models.CharField(max_length=100, blank=True, null=True)
    edited_unit = models.CharField(max_length=20, blank=True, null=True)
    edited_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    # ✅ Verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_results')
    verified_at = models.DateTimeField(blank=True, null=True)

    # ✅ Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='testresult_created_by')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='testresult_updated_by')
    
    class Meta: 
        unique_together = ('advice_entry', 'test_item')
    @property
    def final_result(self):
        return self.edited_result or self.machine_result

    @property
    def final_unit(self):
        return self.edited_unit or self.machine_unit

    class Meta:
        unique_together = ('visit', 'test_item')

# Payment for Diagnostic and Hospital Services can be handled via the Payment model above.
class PaymentMethodType(models.Model):
    name = models.CharField(max_length=50)  # e.g., "bKash"
    code = models.CharField(max_length=20, unique=True)  # e.g., "bkash"
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True)  # Optional UI help
    surcharge_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')


    def __str__(self):
        return self.name
class Payment(models.Model):
    payment_code = models.CharField(max_length=20, unique=True)
    invoice = models.ForeignKey('AdviceInvoice', on_delete=models.CASCADE)
    visit_code = models.CharField(max_length=30)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='++')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.payment_code} - ৳{self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.payment_code:
            today = timezone.localtime().date()
            prefix = f"PMT{today.strftime('%y%m%d')}"
            last = Payment.objects.filter(payment_code__startswith=prefix).order_by('id').last()
            next_number = int(last.payment_code[-4:]) + 1 if last else 1
            self.payment_code = f"{prefix}{next_number:04d}"

        super().save(*args, **kwargs)
class PaymentMethod(models.Model):
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE)
    visit_code = models.CharField(max_length=30)

    method_type = models.ForeignKey('PaymentMethodType', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)            
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return f"{self.method_type.name} - ৳{self.amount}"

class CommissionRule(models.Model):
    CONSULTANT_TYPE_CHOICES = [
        ('internal', 'Internal Consultant'),
        ('external', 'External Consultant'),
        ('referrer', 'Referrer'),
    ]

    APPLY_ON_CHOICES = [
        ('base', 'Base Price'),
        ('final', 'Final Price'),
    ]

    consultant_type = models.CharField(max_length=20, choices=CONSULTANT_TYPE_CHOICES)
    consultant_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    consultant_object_id = models.PositiveIntegerField()
    consultant = GenericForeignKey('consultant_content_type', 'consultant_object_id')

    test_group = models.ForeignKey('TestGroup', on_delete=models.CASCADE)

    commission_type = models.CharField(max_length=10, choices=[('flat', 'Flat'), ('percent', 'Percentage')])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    apply_on = models.CharField(max_length=10, choices=APPLY_ON_CHOICES, default='final')

    version = models.PositiveIntegerField(default=1)
    previous_version = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='next_version')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='+')

    class Meta:
        unique_together = ('consultant_type', 'consultant_content_type', 'consultant_object_id', 'test_group', 'version')

    def __str__(self):
        return f"{self.get_consultant_type_display()} - {self.consultant} | {self.test_group.name} | v{self.version}"

    def calculate(self, base_price, final_price):
        price = base_price if self.apply_on == 'base' else final_price
        return self.value if self.commission_type == 'flat' else (self.value / 100) * price

    def save(self, *args, **kwargs):
        if self.pk:
            old = CommissionRule.objects.get(pk=self.pk)
            changed = (
                old.value != self.value or
                old.commission_type != self.commission_type or
                old.test_group_id != self.test_group_id or
                old.consultant_type != self.consultant_type or
                old.consultant_content_type_id != self.consultant_content_type_id or
                old.consultant_object_id != self.consultant_object_id or
                old.apply_on != self.apply_on
            )
            if changed:
                self.is_active = False
                super().save(*args, **kwargs)
                return CommissionRule.objects.create(
                    consultant_type=self.consultant_type,
                    consultant_content_type=self.consultant_content_type,
                    consultant_object_id=self.consultant_object_id,
                    test_group=self.test_group,
                    commission_type=self.commission_type,
                    value=self.value,
                    apply_on=self.apply_on,
                    version=self.version + 1,
                    previous_version=self,
                    created_by=self.updated_by,
                    updated_by=self.updated_by
                )
        super().save(*args, **kwargs)
        return self

    @classmethod
    def get_active_rule(cls, consultant_type, consultant_instance, test_group):
        return cls.objects.filter(
            consultant_type=consultant_type,
            consultant_content_type=ContentType.objects.get_for_model(consultant_instance),
            consultant_object_id=consultant_instance.id,
            test_group=test_group,
            is_active=True
        ).order_by('-version').first()
