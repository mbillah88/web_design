from django.core.management.base import BaseCommand
from django.db import connections, OperationalError
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from accounts.models import (
    Role, ModuleGroup, Module, Permission, CustomUser,
    Department, Profile, ActionType
)
from diagnostics.models import (
    Consultant, TestCategory, TestSubCategory, TestGroup, TestItem, BedType, PaymentMethodType, TestAccessory
)
from accounts.constants import MODULE_LAYOUT, SUPERADMIN_MODULES


class Command(BaseCommand):
    help = "🎯 Full System Setup: Roles, Users, Modules, Permissions, Diagnostics, BedType, PaymentMethodType"

    def handle(self, *args, **kwargs):
        if not self.check_db():
            return

        call_command('migrate', interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ মাইগ্রেশন সম্পন্ন"))

        self.action_map = self.setup_action_types()
        self.role_map = self.setup_roles()
        self.default_department = self.setup_department()
        self.setup_default_users()
        self.setup_modules()
        self.assign_permissions()
        self.setup_diagnostics()
        self.setup_bed_types()
        self.setup_payment_methods()
        self.setup_consultants()
        self.setup_test_accessories()  # ✅ নতুন ফাংশন কল

        self.stdout.write(self.style.SUCCESS("🎯 সম্পূর্ণ সেটআপ সফলভাবে সম্পন্ন ✅"))

    def check_db(self):
        try:
            connections['default'].ensure_connection()
            self.stdout.write(self.style.SUCCESS("✅ ডাটাবেজ সংযোগ সফল"))
            return True
        except OperationalError:
            self.stdout.write(self.style.ERROR("❌ ডাটাবেজ সংযোগ ব্যর্থ"))
            return False

    def setup_action_types(self):
        keys = ['access', 'create', 'edit', 'delete']
        action_map = {}
        for i, key in enumerate(keys):
            action, _ = ActionType.objects.get_or_create(
                key=key,
                defaults={'name_bn': key.title(), 'order': i}
            )
            action_map[key] = action
        return action_map

    def setup_roles(self):
        names = [
            "SystemAdmin", "Admin", "Receptionist", "LabTechnician", "RadiologyTechnician",
            "Doctor", "AccountsOfficer", "AdmissionOfficer", "IPDBilling",
            "OPDBilling", "NursingStaff", "PharmacyStaff", "InventoryManager",
            "HRManager", "ReportViewer"
        ]
        role_map = {}
        for name in names:
            role, _ = Role.objects.get_or_create(name=name)
            role_map[name] = role
        return role_map

    def setup_department(self):
        dept, _ = Department.objects.get_or_create(name="Diagnostics", code="DIAG")
        return dept

    def setup_default_users(self):
        users = [
            ("admin1", "SystemAdmin"),
            ("admin", "Admin"),
            ("reception", "Receptionist"),
            ("lab", "LabTechnician"),
            ("radiology", "RadiologyTechnician"),
            ("doctor", "Doctor"),
            ("accounts", "AccountsOfficer"),
            ("admission", "AdmissionOfficer"),
            ("ipdbill", "IPDBilling"),
            ("opdbill", "OPDBilling"),
            ("nurse", "NursingStaff"),
            ("pharmacy", "PharmacyStaff"),
            ("inventory", "InventoryManager"),
            ("hr", "HRManager"),
            ("report", "ReportViewer"),
        ]
        for username, role_key in users:
            user, _ = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "is_staff": True,
                    "role": self.role_map[role_key],
                    "password": make_password("123"),
                }
            )
            Profile.objects.get_or_create(user=user, defaults={
                "department": self.default_department,
                "designation": role_key
            })
    
    def to_pascal_case(self, s):
        return ''.join(word.capitalize() for word in s.split('_'))

    def setup_modules(self):
        for group_name, modules in MODULE_LAYOUT.items():
            group, _ = ModuleGroup.objects.get_or_create(name=group_name)
            for parent_url, config in modules.items():
                config = config or {}
                parent, _ = Module.objects.get_or_create(
                    url_name=parent_url,
                    defaults={
                        "name": config.get("label", parent_url.split(":")[-1].replace('_', ' ').title()),
                        "label": config.get("label"),
                        "group": group,
                        "icon": config.get("icon", "bi-speedometer"),
                        "class_name": config.get("class_name"),
                        "is_visible": True,
                        "is_header": config.get("is_header", False),
                        "order": config.get("order", 0)
                    }
                )
                parent.actions.set([self.action_map['access']])

                for child_url in config.get("children", []):
                    inferred = []
                    if 'add' in child_url or 'create' in child_url:
                        inferred.append('create')
                    if 'edit' in child_url:
                        inferred.append('edit')
                    if 'delete' in child_url or 'cancel' in child_url:
                        inferred.append('delete')
                    if 'view' in child_url or 'list' in child_url or 'print' in child_url or 'approve' in child_url:
                        inferred.append('access')
                    if not inferred:
                        inferred = ['access']

                    child, _ = Module.objects.get_or_create(
                        url_name=child_url,
                        defaults={
                            "name": child_url.split(":")[-1].replace('_', ' ').title(),
                            "group": group,
                            "parent": parent,
                            "icon": "bi-circle",
                            "is_visible": False,
                            "is_header": False,
                            "order": 0
                        }
                    )
                    child.actions.set([self.action_map[k] for k in inferred])

    def assign_permissions(self):
        admin = CustomUser.objects.filter(username="admin").first()
        for module in Module.objects.all():
            for action in ActionType.objects.all():
                url_key = module.url_name.split(":")[-1]
                is_allowed = url_key in SUPERADMIN_MODULES

                perm, created = Permission.objects.get_or_create(
                    role=self.role_map["SystemAdmin"],
                    module=module,
                    action=action,
                    defaults={
                        'is_allowed': is_allowed,
                        'created_by': admin,
                        'updated_by': admin,
                    }
                )

                if not created:
                    if is_allowed and not perm.is_allowed:
                        perm.is_allowed = True
                        perm.updated_by = admin
                        perm.save()


    def setup_diagnostics(self):
        admin_user = CustomUser.objects.filter(username="admin").first()

        # Step 1: Categories
        categories = [
            ("Pathology", "Lab-based diagnostic tests"),
            ("Radiology", "Imaging-based diagnostic tests"),
        ]
        category_map = {}
        for name, desc in categories:
            cat, _ = TestCategory.objects.get_or_create(name=name, defaults={
                "description": desc,
                "created_by": admin_user
            })
            category_map[name] = cat

        # Step 2: Subcategories
        subcategories = [
            ("Haematological", "Pathology", "রক্তের কোষ বিশ্লেষণ"),
            ("Biochemical", "Pathology", "রাসায়নিক বিশ্লেষণ"),
            ("Serological", "Pathology", "ভাইরাস ও অ্যান্টিবডি পরীক্ষা"),
            ("Microbiological", "Pathology", "সংক্রমণ শনাক্তকরণ"),
            ("Clinical Pathology", "Pathology", "প্রস্রাব, মল, বডি ফ্লুইড বিশ্লেষণ"),
            ("Histopathology", "Pathology", "টিস্যু বায়োপসি ও ক্যান্সার নির্ণয়"),
            ("Cytological", "Pathology", "কোষ বিশ্লেষণ"),
            ("Immunological", "Pathology", "অটোইমিউন ও অ্যালার্জি পরীক্ষা"),
            ("Hormone", "Pathology", "Hormone Test পরীক্ষা"),
            ("Molecular Diagnostics", "Pathology", "PCR, RT-PCR, COVID-19"),

            ("Digital X-Ray", "Radiology", "ডিজিটাল এক্স-রে"),
            ("USG", "Radiology", "আল্ট্রাসনোগ্রাফি"),
            ("ECHO", "Radiology", "আল্ট্রাসনোগ্রাফি"),
            ("ECG", "Radiology", "আল্ট্রাসনোগ্রাফি"),
            ("CT Scan", "Radiology", "কম্পিউটারাইজড টোমোগ্রাফি"),
            ("MRI", "Radiology", "ম্যাগনেটিক রেজোন্যান্স ইমেজিং"),
            ("Mammography", "Radiology", "স্তন ক্যান্সার স্ক্রিনিং"),
            ("Echocardiography (ECHO)", "Radiology", "হৃদপিণ্ডের আল্ট্রাসাউন্ড"),
            ("Color Doppler", "Radiology", "রক্তপ্রবাহ বিশ্লেষণ"),
            ("DEXA Scan", "Radiology", "হাড়ের ঘনত্ব পরীক্ষা"),
            
            ("Other", "Pathology", "Other পরীক্ষা"),
        ]
        subcategory_map = {}
        for name, cat_name, desc in subcategories:
            subcat, _ = TestSubCategory.objects.get_or_create(name=name, defaults={
                "category": category_map[cat_name],
                "description": desc,
                "created_by": admin_user
            })
            subcategory_map[name] = subcat

        # Step 3: Test Groups
        #Biochemical
        groups = [
            ("1 hrs After Breakfast", "Biochemical", 160, 96, 40),
            ("2 hrs After Breakfast", "Biochemical", 160, 112, 30),
            ("1 hrs After Lunch", "Biochemical", 160, 112, 30),
            ("2 hrs After Lunch", "Biochemical", 160, 112, 30),
            ("1 hrs After Dinner", "Biochemical", 160, 96, 40),
            ("2 hrs After Dinner", "Biochemical", 160, 112, 30),
            ("1 hrs After 75 gm glucose", "Biochemical", 160, 112, 30),
            ("2 hrs After 75 gm glucose", "Biochemical", 160, 112, 30),
            ("1 hrs After Iftar", "Biochemical", 160, 112, 30),
            ("2 hrs After Iftar", "Biochemical", 160, 112, 30),
            ("After Breakfast", "Biochemical", 160, 112, 30),
            ("After Lunch", "Biochemical", 160, 112, 30),
            ("After Dinner", "Biochemical", 160, 112, 30),
            ("Before Lunch", "Biochemical", 160, 112, 30),
            ("Before Iftar", "Biochemical", 160, 112, 30),
            ("Before Dinner", "Biochemical", 160, 112, 30),
            ("Mid Day", "Biochemical", 160, 112, 30),
            ("FBS with CUS", "Biochemical", 160, 112, 30),
            ("FBS (Fasting Blood Sugar)", "Biochemical", 160, 112, 30),
            ("RBS with CUS", "Biochemical", 160, 112, 30),
            ("Fasting Lipid Profile (Four Test)", "Biochemical", 1000, 700, 30),
            ("Random Lipid Profile (Four Test)", "Biochemical", 1000, 600, 40),
            ("ACTH", "Biochemical", 1200, 900, 25),
            ("S.Alkaline Phosphatase (ALP)", "Biochemical", 300, 210, 30),
            ("Alpha Feto Protein (AFP)", "Biochemical", 1200, 840, 30),
            ("ANA Test", "Biochemical", 1200, 840, 30),
            ("ANF", "Biochemical", 1200, 840, 30),
            ("Anti Cardiolipin AB IgG, IgM", "Biochemical", 3000, 2250, 25),
            ("Anti CCP", "Biochemical", 2000, 1500, 25),
            ("Anti DNA (ELISA)", "Biochemical", 1200, 840, 30),
            ("Anti-Double Stranded DNA (Anti-dsDNA)", "Biochemical", 1200, 840, 30),
            ("Anti HAV IgM", "Biochemical", 800, 480, 40),
            ("Anti HBc", "Biochemical", 800, 480, 40),
            ("Anti HBc IgG", "Biochemical", 1200, 960, 20),
            ("Anti Cardiolipin AB IgG,IgM", "Biochemical", 3000, 750, 25),
            ("Anti-HCV (ELISA)", "Biochemical", 1000, 700, 30),
            ("Anti Scl - 70", "Biochemical", 1600, 1120, 30),
            ("Anti HIV", "Biochemical", 1200, 900, 25),
            ("Anti Phospholipid Ab IgG, IgM", "Biochemical", 1600, 1120, 30),
            ("APTT", "Biochemical", 400, 280, 30),
            ("Blood Film", "Biochemical", 200, 140, 30),
            ("Blood For LDH", "Biochemical", 400, 280, 30),
            ("Blood Urea", "Biochemical", 160, 112, 30),
            ("C/S For Ascitic Fluid", "Biochemical", 400, 240, 40),
            ("C/S For Gram Stain", "Biochemical", 400, 240, 40),
            ("C/S of Discharge", "Biochemical", 400, 240, 40),
            ("CCR (Creatinine clearance Rate)", "Biochemical", 600, 408, 32),
            ("CFS-Biochemical", "Biochemical", 350, 210, 40),
            ("CK-MB", "Biochemical", 1200, 804, 33),
            ("CSF C/S", "Biochemical", 400, 240, 40),
            ("DC", "Biochemical", 200, 120, 40),
            ("Estimation of testosterone", "Biochemical", 1200, 720, 40),
            ("FSH (ELISA)", "Biochemical", 1200, 840, 30),
            ("FT3 (ELISA)", "Biochemical", 1200, 840, 30),
            ("FT4 (ELISA)", "Biochemical", 1200, 840, 30),
            ("GTT (3 Samples)", "Biochemical", 800, 480, 40),
            ("GTT (5 Samples)", "Biochemical", 1200, 720, 40),
            ("Growth Hormone", "Biochemical", 1200, 840, 30),
            ("HBA1C", "Biochemical", 1000, 700, 30),
            ("Hbs Ag (ELISA)", "Biochemical", 1000, 700, 30),
            ("Hbs-Ag (Confirmatory)", "Biochemical", 1000, 700, 30),
            ("HDL Cholesterol", "Biochemical", 300, 210, 30),
            ("INR", "Biochemical", 1000, 600, 40),
            ("ICT For Dengue Antibody (IgM & IgG)", "Biochemical", 1000, 600, 40),
            ("ICT For Dengue (IgM & IgG)", "Biochemical", 1200, 804, 33),
            ("LDL Cholesterol", "Biochemical", 300, 210, 30),
            ("Liver Function Test (LFT)", "Biochemical", 900, 630, 30),
            ("Microprotein", "Biochemical", 250, 150, 40),
            ("Microprotein Sugar", "Biochemical", 250, 150, 40),
            ("Na+,K+, Cl-", "Biochemical", 600, 360, 40),
            ("Oestrogen/Estrogen", "Biochemical", 1200, 840, 30),
            ("OGTT", "Biochemical", 600, 360, 40),
            ("P/S for C/S", "Biochemical", 250, 150, 40),
            ("P/S for Gram Stain", "Biochemical", 250, 150, 40),
            ("P/S for Gramstaining", "Biochemical", 250, 150, 40),
            ("Plural Fluid For Analysis", "Biochemical", 1000, 600, 40),
            ("Progesterone", "Biochemical", 1200, 840, 30),
            ("Protein Profile (Four Test)", "Biochemical", 700, 420, 40),
            ("PSA (Prostate-Specific Antigen) ELISA", "Biochemical", 1200, 840, 30),
            ("R.K-39", "Biochemical", 600, 420, 30),
            ("Rubella IgG", "Biochemical", 1200, 840, 30),
            ("S.A/G", "Biochemical", 500, 300, 40),
            ("S.Albumin", "Biochemical", 180, 108, 40),
            ("S.Albumin Globulin Ratio.", "Biochemical", 500, 300, 40),
            ("S.aldolase", "Biochemical", 1000, 600, 40),
            ("S.Amylase", "Biochemical", 800, 536, 33),
            ("S.bilirubin", "Biochemical", 400, 240, 40),
            ("S.Bilirubin (Direct)", "Biochemical", 400, 240, 40),
            ("S.Bilirubin (Indirect+Total+Direct)", "Biochemical", 1200, 720, 40),
            ("S.Bilirubin (Total)", "Biochemical", 400, 240, 40),
            ("S.Bilirubin Indirect.", "Biochemical", 400, 240, 40),
            ("S.C3 Level", "Biochemical", 1200, 900, 25),
            ("S.Calcium", "Biochemical", 500, 340, 32),
            ("S.Cholesterol", "Biochemical", 300, 180, 40),
            ("S.Cortisol (AM)", "Biochemical", 1200, 840, 30),
            ("S.Cortisol (PM)", "Biochemical", 1200, 900, 25),
            ("S.Creatinine", "Biochemical", 400, 240, 40),
            ("S.Electrolytes", "Biochemical", 1000, 1000, 0),
            ("S.Ferritin", "Biochemical", 1000, 1000, 0),
            ("S.Globulin", "Biochemical", 180, 108, 40),
            ("S.IgE", "Biochemical", 1200, 720, 40),
            ("S.Iron", "Biochemical", 1000, 600, 40),
            ("S.Iron Profile", "Biochemical", 3200, 2240, 30),
            ("S.LDH", "Biochemical", 1000, 600, 40),
            ("S.LH", "Biochemical", 1200, 840, 30),
            ("S.Lipase", "Biochemical", 1000, 700, 30),
            ("S.Phosphate PO4", "Biochemical", 400, 240, 40),
            ("S.TIBC", "Biochemical", 1000, 600, 40),
            ("S.Total Protein", "Biochemical", 180, 108, 40),
            ("S.Triglyceride", "Biochemical", 350, 210, 40),
            ("S.Urea", "Biochemical", 400, 240, 40),
            ("S.Uric Acid", "Biochemical", 550, 330, 40),
            ("S.Urin Amylase.", "Biochemical", 550, 330, 40),
            ("S.Copper", "Biochemical", 1000, 750, 25),
            ("S.Ceruloplasmin Level", "Biochemical", 1500, 1200, 20),
            ("S.Protein Electrophoresis", "Biochemical", 1500, 1200, 20),
            ("S.Tg Level (Thyroglobulin)", "Biochemical", 2000, 1600, 20),
            ("S.IgG", "Biochemical", 1000, 200, 20),
            ("S.eGFR (Estimated Glomerular Filtration Rate)", "Biochemical", 1200, 900, 25),
            ("S.Total Iron", "Biochemical", 1000, 600, 40),
            ("SGOT (AST)", "Biochemical", 500, 340, 32),
            ("SGPT (ALT)", "Biochemical", 500, 340, 32),
            ("Spot PCR (Protein Creatinen Ratio)", "Biochemical", 450, 270, 40),
            ("Spot Urinary Protein", "Biochemical", 500, 300, 40),
            ("T3 (ELISA)", "Biochemical", 900, 630, 30),
            ("T4 (ELISA)", "Biochemical", 900, 630, 30),
            ("Throat Swab For C/S", "Biochemical", 800, 640, 20),
            ("Thyroid Anti Body", "Biochemical", 1000, 700, 30),
            ("TPHA", "Biochemical", 800, 480, 40),
            ("TORCH IgM/IgG (10 Test)", "Biochemical", 8000, 6000, 25),
            ("Troponin I", "Biochemical", 900, 540, 40),
            ("Tryglyceride (TG)", "Biochemical", 400, 280, 30),
            ("TSH (ELISA)", "Biochemical", 900, 630, 30),
            ("Urethral Discharge for Gram -stain", "Biochemical", 250, 150, 40),
            ("Urethral Mass C/S", "Biochemical", 800, 640, 20),
            ("Urine ACR", "Biochemical", 1200, 1008, 16),
            ("Urine PCR", "Biochemical", 1200, 1008, 16),
            ("Urine For Amylase", "Biochemical", 600, 360, 40),
            ("Urine For C/S", "Biochemical", 800, 640, 20),
            ("Urine for Gagulation", "Biochemical", 400, 240, 40),
            ("Urine For Mycro-Albumin", "Biochemical", 300, 180, 40),
            ("Urine For Reducing Substance", "Biochemical", 400, 368, 40),
            ("Urine R/E", "Biochemical", 160, 112, 30),
            ("Urine for Phosphates", "Biochemical", 600, 480, 20),
            ("UTV (Urinary Total Volume)", "Biochemical", 1000, 600, 40),
            ("UTP (Urinary total protein) 24 hrs", "Biochemical", 1000, 750, 25),
            ("Wound Swab For C/S", "Biochemical", 800, 640, 20),
            ("D-Dimer", "Biochemical", 1000, 600, 40),
            ("Blood C/S", "Biochemical", 800, 640, 20),
            ("HBV DNA (PCR)", "Biochemical", 6000, 3600, 25),
            ("C-Peptide (Fasting)", "Biochemical", 1700, 1190, 30),
            ("NT-proBNP", "Biochemical", 3000, 2100, 30),
            ("ICT Micro Filaria (Elisa)", "Biochemical", 1200, 960, 20),
            ("Dengue IgG/IgM (Govt fixed rate)", "Biochemical", 1000, 800, 20),
            ("Outsample (Blood) Collection", "Biochemical", 200, 200, 0),
            ("Insulin Level (Fasting)", "Biochemical", 600, 480, 20),
            ("Urine for Copper", "Biochemical", 1500, 1200, 20),
            ("C ANCA", "Biochemical", 1500, 1200, 20),
            ("P ANCA", "Biochemical", 1500, 1200, 20),
            ("CSF for Biochemistry, Cytology", "Biochemical", 1200, 960, 20),
            ("CSF for ADA", "Biochemical", 1300, 1040, 20),
            ("RFT (S.Creatinine+S.Urea)", "Biochemical", 900, 540, 40),

        ]
        #Haematological
        groups += [
            ("AMH (Anti- Mullerian Hormone)", "Haematological", 3000, 2700, 10),
            ("MCHC", "Haematological", 330, 297, 10),
            ("Blood For MP", "Haematological", 1200, 1080, 10),
            ("Haemoglobin Hb%", "Haematological", 250, 225, 10),
            ("Hb-Electrophoresis", "Haematological", 1500, 900, 40),
            ("Anti HBs", "Haematological", 1000, 900, 10),
            ("Antinuclear Antibody (ANA)", "Haematological", 1000, 900, 10),
            ("PBF (Peripheral Blood Film Study)", "Haematological", 500, 450, 10),
            ("BT CT", "Haematological", 300, 270, 10),
            ("Prolactin", "Haematological", 1200, 1080, 10),
            ("TRAB (Tsh Receptor Antibody)", "Haematological", 8000, 7200, 10),
            ("CBC (Complete Blood Count)", "Haematological", 400, 400, 0),
            ("PT (Prothrombin Time)", "Haematological", 800, 720, 10),
            ("Testosterone", "Haematological", 1200, 1080, 10),
            ("R.A Test", "Haematological", 600, 540, 10),
            ("TCE (Total Circulating Eosinophil)", "Haematological", 300, 270, 10),
            ("TC,DC,ESR", "Haematological", 200, 180, 10),
            ("ESR", "Haematological", 200, 180, 10),
            ("H.Pylori", "Haematological", 1000, 900, 10),
            ("TC,DC", "Haematological", 150, 135, 10),
            ("LH (ELISA)", "Haematological", 1200, 1080, 10),
            ("Platelet Count", "Haematological", 250, 225, 10),
            ("Lupus Anticoagulant (LA)", "Haematological", 1200, 1080, 10)
        ]
        #Serological
        groups += [
            ("Anti Hbe (Elisa)", "Serological", 1200, 840, 30),
            ("Urinary Amylase", "Serological", 600, 360, 40),
            ("Toxoplasma Gondi (IgG)", "Serological", 1000, 700, 30),
            ("Urine For Albumin", "Serological", 300, 180, 40),
            ("Urine For bence-jones Protein", "Serological", 250, 150, 40),
            ("Urine for Ketone body", "Serological", 400, 300, 25),
            ("Sputum For A.F.B. 2 SAMPLE", "Serological", 1200, 720, 40),
            ("Urine for PCR", "Serological", 800, 656, 18),
            ("Urine For Pregnancy", "Serological", 250, 162, 35),
            ("Sputam for Eosinophil", "Serological", 200, 160, 20),
            ("Stool R/E", "Serological", 300, 180, 40),
            ("VDRL (Qualitive)", "Serological", 500, 320, 36),
            ("VDRL (Quantitive)", "Serological", 500, 300, 40),
            ("Vit B12", "Serological", 2500, 2000, 20),
            ("Widal Test", "Serological", 500, 300, 40),
            ("Seram Toxoplasma Elaisa", "Serological", 1000, 750, 25),
            ("Anty HCV (Screening)", "Serological", 1200, 756, 37),
            ("S.Lithium", "Serological", 1000, 600, 40),
            ("S.IGM", "Serological", 1200, 1008, 16),
            ("S.Albumin Ratio (Next)", "Serological", 125, 75, 40),
            ("Rubella (IgM)", "Serological", 1200, 840, 30),
            ("Rh-antibody titre", "Serological", 1000, 600, 40),
            ("S.Folic Acid", "Serological", 2000, 1600, 20),
            ("Prostatic smear for Gram stainnig", "Serological", 600, 360, 40),
            ("P/S For R/E", "Serological", 240, 144, 40),
            ("Dengue NS1 Antigen", "Serological", 1200, 1200, 0),
            ("Dengue NS1 (Govt fixed rate)", "Serological", 300, 300, 0),
            ("CSF Analysis", "Serological", 1200, 1200, 0),
            ("Urine for ACR", "Serological", 1200, 1008, 16),
            ("Anti HAV", "Serological", 1200, 780, 35),
            ("HCV RNA", "Serological", 10000, 8000, 20),
            ("ICT-Filaria", "Serological", 1200, 804, 33),
            ("ICT -TB", "Serological", 1000, 600, 40),
            ("ICT For Malaria", "Serological", 1200, 804, 33),
            ("HCV (Antibody)", "Serological", 850, 510, 40),
            ("HbsAg (Screening)", "Serological", 500, 350, 30),
            ("Anti RNP Antibody", "Serological", 2500, 2000, 20),
            ("HBe Ag", "Serological", 1200, 780, 35),
            ("H.Pylori (IgG,IgM)", "Serological", 2000, 1400, 30),
            ("FNAC", "Serological", 1500, 1275, 15),
            ("Fluid For C/S", "Serological", 800, 600, 25),
            ("Triple/Febrile Antizen", "Serological", 1100, 660, 40),
            ("Dengue (IgM/IgG)", "Serological", 900, 900, 0),
            ("CRP (Govt fixed rate)", "Serological", 600, 600, 0),
            ("HLA B-27", "Serological", 4000, 3000, 25),
            ("Anti HBe Ag", "Serological", 1000, 650, 35),
            ("Urine For Electrolyte", "Serological", 1600, 1280, 20),
            ("S. Lactate", "Serological", 1600, 1280, 20),
            ("CFT For Filaria", "Serological", 650, 390, 40),
            ("Screening & Crossmatch", "Serological", 1000, 1000, 0),
            ("Blood Grouping", "Serological", 150, 90, 40),
            ("ASO Titre", "Serological", 500, 300, 40),
            ("Ascitic Fluid  Analysis", "Serological", 2500, 2250, 10),
            ("Anti H-Pylori IgG", "Serological", 1000, 600, 40),
            ("T.P.H.A.", "Serological", 800, 480, 40)
        ]
        #Cytological
        groups += [
            ("Anti HBe Total", "Cytological", 1200, 1080, 10),
            ("CSF  cytolygy, Biochemistry", "Cytological", 1000, 900, 10),
            ("urine for AFB (3days)", "Cytological", 368, 331, 10),
            ("Biopsy (Medium) - (The Lab)", "Cytological", 2500, 2500, 0),
            ("CSF for biochemistry", "Cytological", 340, 306, 10),
            ("Biopsy (Large)", "Cytological", 3500, 3500, 0),
            ("Biopsy (Small)", "Cytological", 1200, 1200, 0),
            ("Synovil Fluid Analysis", "Cytological", 1000, 900, 10),
            ("Biopsy (Small) - (The Lab)", "Cytological", 1350, 1350, 0),
            ("Total protin (Urine)", "Cytological", 350, 315, 10),
            ("S.Cytology(Malignant Cell)", "Cytological", 500, 450, 10),
            ("Stool C/S", "Cytological", 400, 360, 10),
            ("Biopsy (Medium)", "Cytological", 2000, 2000, 0),
            ("Pap's smear", "Cytological", 1200, 1200, 0),
            ("Biopsy (Large) - (The Lab)", "Cytological", 4250, 4250, 0)
        ]
        #Clinical Pathology
        groups += [
            ("Body Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("CSF R/E", "Clinical Pathology", 400, 240, 40),
            ("Pleural Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("Ascitic Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("Semen for AFB", "Clinical Pathology", 600, 360, 40),
            ("Synovial Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("Amniotic Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("Peritoneal Fluid R/E", "Clinical Pathology", 400, 240, 40),
            ("CSF for AFB", "Clinical Pathology", 600, 360, 40),    
            ("Pregnancy Test (Serum)", "Clinical Pathology", 400, 240, 40)
        ]
        #Microbiological
        groups += [
            ("Sputam for afb", "Microbiological", 600, 360, 40),
            ("Sputum For Malignancy", "Microbiological", 500, 300, 40),
            ("Semen Analysis", "Microbiological", 700, 504, 28),
            ("Sputum for AFB 3 Sample", "Microbiological", 1800, 1080, 40),
            ("Pus for C/S", "Microbiological", 1000, 900, 10),
            ("Stool for Reducing Substance", "Microbiological", 100, 60, 40),
            ("Gram Staining", "Microbiological", 350, 210, 40),
            ("Sputam C/S", "Microbiological", 800, 640, 20),
            ("Toxoplasma Gondi (IgM)", "Microbiological", 1000, 700, 30),
            ("Anti HEV IgM", "Microbiological", 1200, 840, 30),
            ("Anti mitochondrial antibody", "Microbiological", 3000, 2550, 15),
            ("Nail Scraping for fungus", "Microbiological", 250, 150, 40),
            ("Stool for OBT", "Microbiological", 400, 240, 40),
            ("ICT FOR Kala zar", "Microbiological", 1200, 720, 40),
            ("Anti liver kidney microsomal antibody", "Microbiological", 3200, 2720, 15),
            ("Anti smooth muscle antibody", "Microbiological", 4000, 3400, 15),
            ("Swab for c/s", "Microbiological", 800, 640, 20),
            ("Skin Scraping for Fungus", "Microbiological", 250, 150, 40),
            ("MT Test (Tuberculin Test)", "Microbiological", 350, 210, 40),
            ("Urine for chyle", "Microbiological", 800, 800, 0)
        ]
        #Immunological
        groups += [
            ("Cancer Antigen (CA) - 125", "Immunological", 1200, 840, 30),
            ("Cancer Antigen (CA) - 15.3", "Immunological", 1200, 840, 30),
            ("Cancer Antigen (CA) - 19.9", "Immunological", 1200, 840, 30),
            ("CEA (Carcinoembryonic Antigen)", "Immunological", 1200, 840, 30),
            ("Complement C3", "Immunological", 1200, 1080, 10),
            ("Complement C4", "Immunological", 1200, 1080, 10),
            ("Creatine phosphokinase (CPK)", "Biochemical", 1000, 700, 30),
            ("25 (OH) Vitamin D", "Immunological", 3000, 2250, 25),
            ("PTH (Para Thyroid Hormone)", "Immunological", 1500, 1200, 20),
            ("Anti Thyroid Antibody (Anti TPO + Anti TG)", "Immunological", 2400, 1440, 40),
            ("PTH", "Immunological", 1500, 1200, 20),
            ("Anti Hbc IgM", "Immunological", 1200, 960, 20),
            ("Blood Grouping and Cross Matching", "Immunological", 1000, 1000, 0),
            ("Beta-hCG", "Immunological", 1200, 840, 30),
            ("Anti TPO Antibody", "Immunological", 1200, 840, 30),
            ("Anti TG Antibody", "Immunological", 1200, 840, 30),
            ("Anti-acetylcholine receptor (AChR)", "Immunological", 3570, 2856, 20),
            ("ENA Profile", "Immunological", 8000, 6000, 25),
            ("Blood Coomb's test", "Immunological", 1500, 1200, 20),
            ("Anti Hbs Ag Titre", "Immunological", 1200, 960, 20),
            ("Anti- Muscle-Kinase(Anti MuSK)", "Immunological", 3500, 2800, 20),
            ("TORCH panel (IgG & IgM)", "Immunological", 8000, 6000, 25)

        ]
        #Hormone
        groups += [
            ("S.Oestrogen / Estradiol / Estrogen", "Hormone", 1200, 1080, 10),
            ("S.Magnesium", "Hormone", 1200, 1080, 10),
            ("S.Copper", "Hormone", 2500, 2250, 10)
        ]
        # USG
        groups += [
            ("Anomaelly Scanning", "USG", 2000, 1800, 10),
            ("Asperation/trucnt biopsy", "USG", 2000, 1800, 10),
            ("Breast (Both) USG", "USG", 1600, 1440, 10),
            ("Breast. Single USG", "USG", 1000, 900, 10),
            ("Duplex Stady of (RT) Lower Limb Vessels", "USG", 2800, 2520, 10),
            ("HBS USG", "USG", 950, 855, 10),
            ("KUB & PVR USG", "USG", 1100, 990, 10),
            ("KUB ENCLUDING MCC &PVR USG", "USG", 1100, 990, 10),
            ("KUB USG", "USG", 950, 855, 10),
            ("Lower Abdomen USG", "USG", 950, 855, 10),
            ("Pelvic Region USG", "USG", 1000, 900, 10),
            ("Scrotum USG", "USG", 1200, 1080, 10),
            ("T.V.S(Pelvic Organ)", "USG", 1900, 1710, 10),
            ("Testis USG", "USG", 1200, 1080, 10),
            ("Thyroid USG", "USG", 1400, 1260, 10),
            ("Ultrasound-Guided", "USG", 1500, 1350, 10),
            ("USG  OF THIGH (RT)", "USG", 1200, 1080, 10),
            ("USG Both Breast", "USG", 1500, 1350, 10),
            ("USG Color Doppler of Penis", "USG", 1500, 1350, 10),
            ("USG Of Breast (LT)", "USG", 1000, 900, 10),
            ("USG of Breast (RT)", "USG", 1000, 900, 10),
            ("USG Of Knee (Rt)", "USG", 1200, 1080, 10),
            ("USG Of Neck", "USG", 1000, 900, 10),
            ("USG Of scortum", "USG", 1200, 1080, 10),
            ("USG Of Submandibular Region (RT)", "USG", 1400, 1260, 10),
            ("USG Of Swelling on Lt Upper Limb", "USG", 1400, 1260, 10),
            ("USG Thigh", "USG", 1200, 1080, 10),
            ("USG Thyroid", "USG", 1400, 1260, 10),
            ("USG TVS", "USG", 1500, 1350, 10),
            ("USG of Brain", "USG", 1500, 1350, 10),
            ("USG of Breast (LT)", "USG", 1000, 900, 10),
            ("USG of Pregnancy Profile", "USG", 950, 855, 10),
            ("USG of Scroutum of Doppler", "USG", 2000, 1800, 10),
            ("USG of Submandibular Region (RT)", "USG", 1400, 1260, 10),
            ("USG of Swelling on Lt Upper Limb", "USG", 1400, 1260, 10),
            ("Usg Of Chest", "USG", 1300, 1170, 10),
            ("Usg of Brain", "USG", 1500, 1350, 10),
            ("Usg of left hip to exclude bursitis", "USG", 1500, 1350, 10),
            ("W/A Including MCC & PVR USG", "USG", 1100, 990, 10),
            ("Whole Abdomen", "USG", 1000, 900, 10),
            ("Whole Abdomen OF KUB", "USG", 1000, 900, 10),
            ("USG of Lower Abdomen", "USG", 1000, 900, 10),
            ("duplex stady of (Lt) lower limb vessels", "USG", 2800, 2520, 10),
        ]
        # ECG ECHO
        groups += [
            ("ECG in All Leads. Digital", "ECG", 350, 315, 10),
            ("CTG", "ECHO", 1000, 900, 10),
            ("Echo Cardiogram (2D & M-Mode)", "ECHO", 1200, 1080, 10),
            ("Echo Cardiogram Color Doppler", "ECHO", 2300, 2070, 10)
        ]
        #  X-Rays
        groups += [
            #🫁 Chest X-Rays
            ("Chest P/A view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Chest A/P view - X-Ray", "Digital X-Ray", 600, 540, 10),
            ("Chest including (LT) Clavicle A/P view X-ray.", "Digital X-Ray", 400, 360, 10),
            ("Chest P/A & Oblique View ( Lt)", "Digital X-Ray", 600, 540, 10),
            ("Chest P/A Including Both Clavical B/V", "Digital X-Ray", 600, 540, 10),
            ("Chest P/A view - X-Ray (Covid 19 S.Pack)", "Digital X-Ray", 400, 360, 10),
            ("Chest Lataral View - Xray", "Digital X-Ray", 400, 360, 10),
            ("Chest including Throught - X-Ray", "Digital X-Ray", 350, 315, 10),
            #🦴 Spine X-Rays
            ("L/S Spine B/V X- Ray -1 Flim", "Digital X-Ray", 400, 360, 10),
            ("L/S Spine A/P view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("L/S Spine B/V & S.I Joint", "Digital X-Ray", 800, 720, 10),
            ("L/S Spine Include (Rt) Hip Jt B/V- X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Thoracic Spine B/V - X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Dorso Lumber Spine B/V  X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Thoracis Spine Lataral view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Dorsal Spine A/P view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Cervical Spine A/P View - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Cervical Spine Oblique view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Cervical Spine Lat. view -  X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Cervical Spine Both Oblique Views - X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Sacram Cocyx A/P & Lat. X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Coccyc Sacram B/V - X-Ray", "Digital X-Ray", 800, 720, 10),
            #🧍‍♂️ Abdomen & Pelvis
            ("X- Ray Abdomen E/P", "Digital X-Ray", 400, 360, 10),
            ("Abdomen for Fetal Position - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Abdomen KUB rigion - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("KUB (In Single Film) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("KUB X-Ray (100%)", "Digital X-Ray", 800, 720, 10),
            ("KUB including Pelvis A/P View X-ray.", "Digital X-Ray", 400, 360, 10),
            ("KUB Region (In two films) - X-Ray", "Digital X-Ray", 600, 540, 10),
            ("Pelvis AP view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Pelvis B/V - X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Pelvis B/V - X-Ray (100%)", "Digital X-Ray", 800, 720, 10),
            ("Pelvis include Hip Both joint A/P view - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Pelvis Both Hip Joint AP View & Knee Joint", "Digital X-Ray", 400, 360, 10),
            ("Pelvis showing both Hip joints AP view -X-Ray", "Digital X-Ray", 500, 450, 10),
            #🦵 Lower Limb
            ("Hip Joint B/V Both - X-Ray", "Digital X-Ray", 800, 720, 10),
            ("Hip B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Hip B/V (Lt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Thigh B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Thigh including  Hip & Knee B/V X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Knee A/P view X-Ray (LT)", "Digital X-Ray", 400, 360, 10),
            ("Knee joint B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Knee joint B/V (Lt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Knee include. Thigh B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Knee include. Thigh B/V (Lt) - X-ray", "Digital X-Ray", 400, 360, 10),
            ("Leg incld. Ankle B/V (Lt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Leg including Ankle B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Ankle Joint B/V (Rt) - Xray", "Digital X-Ray", 400, 360, 10),
            ("Ankle Joint B/V (Lt) - Xray", "Digital X-Ray", 400, 360, 10),
            ("Foot B/V (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Foot B/V (Lt)- X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Foot AP view (Rt) - X-Ray", "Digital X-Ray", 400, 360, 10),
            ("Foot AP view (Lt)  X- Ray", "Digital X-Ray", 400, 360, 10),
            ("Foot Lataral view (Rt) - X- Ray", "Digital X-Ray", 400, 360, 10),
            ("Foot Lataral view (Lt) - X- Ray", "Digital X-Ray", 400, 360, 10)
        ]
        group_map = {}
        for name, subcat_name, price, d_price, p_discount in groups:
            group, _ = TestGroup.objects.get_or_create(name=name, defaults={
                "sub_category": subcategory_map[subcat_name],
                "price": price,
                "discounted_price": d_price,
                "percent_discount": p_discount,
                "created_by": admin_user
            })
            group_map[name] = group

        # Step 4: Test Items
        test_items_data = [
            ("1 hrs After 75 gm glucose", "mg/dl", "mmol/L", "<140 mg/dl (<7.8 mmol/L) Normal"),
            ("2 hrs After 75 gm glucose", "mg/dl", "mmol/L", "<140 mg/dl (<7.8 mmol/L) Normal"),
            ("ACR", "mg/dl", "", "<3.00 mg/dl"),
            ("Albumin - Globulin Ratio", "", "", "2.5:1-1:2:1"),
            ("BUN", "mg/dl", "mmol/L", "7-18 mg/dl (2.5-6.4 mmol/L)"),
            ("C.S.F Protein", "", "", ""),
            ("CK-MB", "", "", "Upto 25 U/L"),
            ("Corres. Urine Sugar (IGT)", "", "", "140-200 mg/dl (7.8-11.1 mmol/L)"),
            ("Corres. Urine Sugar (Diabetic)", "", "", ">200 mg/dl (>11.1 mmol/L)"),
            ("Corres. Urine Sugar (Suspicious)", "", "", "110-125 mg/dl (6.1-6.9 mmol/L)"),
            ("Corres. Urine Sugar (Diabetic)", "", "", ">126 mg/dl (>7.0 mmol/L)"),
            ("CPK", "", "", "Women: Up to 170 U/L"),
            ("Creatinine Clearance Rate (CCR)", "ml/min", "", "70-140 ml/min"),
            ("D-Dimer", "", "", "<0.50 mg/L"),
            ("Estimated GFR", "ml/min/1.73m2", "", "90-130 ml/min/1.73m2"),
            ("FASTING LIPID PROFILE (Four Test)", "", "", ""),
            ("Fasting Serum Glucose (FSG)", "mg/dl", "mmol/L", "3.80 - 5.80 %"),
            ("Lipase", "", "", "60-200 IU/L at 37°C"),
            ("Liver Function Tests (LFT)", "", "", ""),
            ("Microalbumin", "mg/dl", "", "<25 mg/L"),
            ("Mid Day", "mg/dl", "mmol/L", "<140 mg/dl (<7.8 mmol/L) Normal"),
            ("Random Blood Sugar (R.B.S)", "mg/dl", "mmol/L", "<140 mg/dl (<7.8 mmol/L) Normal"),
            ("S.Acid Phosphatase", "", "", "3.5-5.0 U/L"),
            ("S.Albumin", "", "", "3.50-5.50 g/dl"),
            ("S.Alkaline Phosphatase", "", "", "30-120 U/L"),
            ("S.Bilirubin (Total)", "mg/dl", "", "0.20-1.00 mg/dl"),
            ("S.Bilirubin (Direct)", "mg/dl", "", "0.00-0.20 mg/dl"),
            ("S.Bilirubin (Total)", "mg/dl", "", "Adult: 0.3-1.0 mg/dl, Newborn: 0.1-2.0 mg/dl"),
            ("S.Cholesterol (Total)", "mg/dl", "mmol/L", "150-200 mg/dl (3.9-5.2 mmol/L), >200-239 mg/dl (5.2-6.2 mmol/L) Borderline High"),
            ("S.Creatinine", "mg/dl", "mmol/L", "Male: 0.60-1.40 mg/dl (53.04-123.7 µmol/L), Female: 0.5-1.20 mg/dl (44.2-106.0 µmol/L)"),
            ("S.Electrolytes", "", "", ""),
            ("S.Ferritin", "ng/ml", "", "Male: 27.00-370.00 ng/ml, Female: 10.00-165.00 ng/ml"),
            ("S.G.O.T (AST)", "", "", "Upto 40 U/L"),
            ("S.G.P.T (ALT)", "", "", "Upto 45 U/L"),
            ("S.Globulin", "g/dl", "", "2.6-3.5 g/dl"),
            ("S.HDL", "mg/dl", "mmol/L", "≥60 mg/dl (≥1.55 mmol/L) No Risk for CHD, 40-60 mg/dl (1.03-1.55 mmol/L) Standard Risk"),
            ("S.Iron", "mg/dl", "", "Men: 65-175 µg/dl, Women: 40-155 µg/dl"),
            ("S.LDL", "mg/dl", "mmol/L", "<100 mg/dl (<2.6 mmol/L) Optimal, 100-129 mg/dl (2.6-3.3 mmol/L) Near Optimal"),
            ("S.Lithium", "", "", "1.5-5.0 mmol/L"),
            ("S.Phosphate (PO4)", "mg/dl", "", "2.5-4.5 mg/dl"),
            ("S.TIBC", "µg/dl", "", "200.00-400.00 µg/dl"),
            ("S.Total Protein", "g/dl", "", "Adults: 6.0-8.0 g/dl, Child: 5.20-9.10 g/dl"),
            ("S.Triglyceride", "mg/dl", "mmol/L", "<150 mg/dl (1.70 mmol/L) Normal, 150-199 mg/dl (1.70-2.25 mmol/L) Borderline High"),
            ("S.Urea", "mg/dl", "", "10-50 mg/dl"),
            ("S.Uric Acid", "mg/dl", "mmol/L", "Male: 3.4-7.0 mg/dl (200-420 µmol/L), Female: 2.4-5.7 mg/dl (140-340 µmol/L)"),
            ("Serum Urea", "", "", ""),
            ("Sugar Glucose 1 hrs after Breakfast", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 1 hrs after Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 1 hrs after Iftar", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 1 hrs Before Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 1 hrs Before Lunch", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 2h after B.F.", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 2h after Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 2h after Iftar", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 2h Before Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose 2h Before Lunch", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose After Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Sugar Glucose Before Dinner", "mg/dl", "mmol/L", "<150 mg/dl (<8.3 mmol/L)"),
            ("Troponin-I", "", "", ""),
            ("Urinary creatinine level", "mg/dl", "mmol/L", "0.40 - 0.90 g/L"),
            ("Urine Creatinine", "mg/dl", "mmol/L", "Male: 0.6-1.2 mg/dl (53.04-106.08 µmol/L), Female: 0.6-1.1 mg/dl (53.0-97.2 µmol/L)"),
            ("Urine Volume", "", "", ""),
            ("Acetone", "", "", ""),
            ("Albumin", "", "", ""),
            ("Bile Pigments", "", "", ""),
            ("Bile Salt", "", "", ""),
            ("Excess of Phosphate", "", "", ""),
            ("Ratio", "", "", ""),
            ("Reaction", "", "", ""),
            ("Reducing Substance", "", "", ""),
            ("Stool for Occult Blood Test (OBT)", "", "", ""),
            ("Sugar/Reducing Substance", "", "", ""),
            ("Urine for Uric Acid", "", "", ""),
            ("Urobilinogen", "", "", ""),
            ("Endocervical Swab for M/E", "", "", ""),
            ("PBF (Peripheral Blood Film Study)", "", "", ""),
            ("APTT", "", "", "26.1-42 Second"),
            ("Atypical cell", "", "", ""),
            ("Basophils", "%", "", ""),
            ("Bleeding Time (B.T)", "", "", "Normal: 2-7 min"),
            ("Circulating Eosinophils", "/cmm", "", "Up to 400 /cmm"),
            ("Circulating Eosinophils", "", "", ""),
            ("Clotting Time (C.T)", "", "", "Normal: 5-11 min"),
            ("Differential Count of", "", "", ""),
            ("E.S.R", "mm in 1st hr", "", "Male: 0-10 mm of 1st hour, Female: 0-20 mm of 1st hour"),
            ("Haemoglobin (Hb%)", "g/dl", "", "Male: 12-18 g/dl, Female: 11-16 g/dl"),
        
            ("Index", "%", "", ""),
            ("INR", "", "", ""),
            ("ISI", "", "", ""),
            ("LE Cell Detection", "", "", ""),
            ("Lymphocytes", "", "", ""),
            ("Malarial Parasite (MP)", "", "", ""),
            ("Malarial Parasite", "", "", ""),
            ("MCHC", "", "", ""),
            ("MCV", "", "", ""),
            ("Meta Myelocyte", "", "", ""),
            ("Monocytes", "", "", ""),
            ("Neutrophils", "%", "", ""),
            ("Others", "%", "", ""),
            ("PCV", "%", "", ""),
            ("Platelets", "/cumm", "", ""),
            ("Prothrombin Time", "Sec", "", ""),
            ("R.B.C", "cmm", "", ""),
            ("Ratio", "", "", ""),
            ("Red Cell Indices", "", "", ""),
            ("Reticulocytes", "%", "", ""),
            ("Test", "", "", ""),
            ("Total Count of W.B.C", "cmm", "", ""),
            ("HBS Ag (Confirmatory)", "", "", "1"),
            ("AFP", "", "", ""),
            ("Anti-ds-DNA", "", "", ""),
            ("HIV", "", "", ""),
            ("ABO System", "", "", ""),
            ("Blood For FDP", "", "", ""),
            ("Blood Group", "", "", ""),
            ("Coomb’s Test", "", "", ""),
            ("Direct", "", "", ""),
            ("Indirect", "", "", ""),
            ("Opinion", "", "", ""),
            ("Referance Value", "", "", ""),
            ("RH-Antibody Detection", "", "", ""),
            ("Rh-System", "", "", ""),
            ("Anti-Mullerian Hormone (AMH)", "ng/ml", "", "20-24 Years: 1.13-11.46 ng/ml"),
            ("NT-PROBNP", "pg/ml", "", "Cut off heart failure: 100pg/ml"),
            ("Cut off Index", "", "", ""),
            ("Sample Index", "", "", ""),
            ("25 (OH) Vitamin D", "ng/ml", "", "Deficient: ≤ 20 ng/ml, Insufficient: < 20 - 30 ng/ml, Sufficient: ≥ 30 ng/ml"),
            ("Aldehyde Test", "", "", ""),
            ("ANA", "IU/ml", "", "< 40 UA/ml"),
            ("Anti CCP Ab", "IU/ml", "", "Normal: < 25.00 IU/ml"),
            ("Anti HCV (ELISA)", "", "", ""),
            ("Anti-HBS Antibody", "", "", ""),
            ("Beta HCG", "mIU/ml", "", "Male & Non-Pregnant < 5.00 mIU/ml"),
            ("C.F.T for Kala-azar/Filaria", "", "", ""),
            ("Ca-125", "U/ml", "", "< 35 U/ml"),
            ("Carcinoembryonic Antigen (CEA)", "ng/ml", "", "Non-Smoker: < 5.00 ng/ml, Smoker: < 10.00 ng/ml"),
            ("Epstein Antibody IgG & IgM", "", "", ""),
            ("Estrogen", "pg/ml", "", "Males: 40.0 - 94.00 pg/ml, Females: Follicular phase: 90 - 174 pg/ml"),
            ("Follicle Stimulating Hormone (FSH)", "IU/L", "", "Female: Follicular Phase: 2.80-11.30 IU/L"),
            ("Free Thyroxine (FT4)", "ng/dl", "", "0.93-1.70 ng/dl"),
            ("Free Tri-iodothyronine (FT3)", "pg/ml", "", "2.30-4.20 pg/ml"),
            ("Growth Hormone", "ng/ml", "", "Adults: < 10.00 ng/ml, Children: < 20.00 ng/ml"),
            ("Hbs Ag (ELISA)", "", "", ""),
            ("HIV I & II", "", "", ""),
            ("Immunochromatographic Test (ICT)", "", "", ""),
            ("Luteinizing Hormone (LH)", "IU/L", "", "Male: 0.80-7.60 IU/L, Female: Follicular Phase: 1.10-11.60 IU/L"),
            ("Mantoux Test", "", "", ""),
            ("Parathyroid Hormone (PTH)", "pg/ml", "", "11.10 - 79.50 pg/ml"),
            ("Progesterone", "ng/ml", "", "Male: ≤ 0.25-0.56 ng/ml, Female: Follicular Phase: ≤ 0.25-0.54 ng/ml"),
            ("Prolactine", "ng/ml", "", "Male: 2.50 - 17.00 ng/ml, Female: 1.90 - 25.00 ng/ml"),
            ("PSA (ELISA)", "ng/ml", "", "< 4.00 ng/ml"),
            ("S.Cortisol (AM)", "nmol/L", "", "7:00 ~ 10:00 a.m 31* 536.54 nmol/L"),
            ("S.Cortisol (PM)", "nmol/L", "", "4:00 ~ 8:00 p.m 77* 317 nmol/L"),
            ("S.IgE", "IU/ml", "", "3 Year: 1.00 - 46.00 IU/ml, 4 - 16 Years: 1.00 - 280.00 IU/ml"),
            ("Testosterone", "nmol/L", "", "Adult Men: 8.70-36.40 nmol/L, Adult Women: 0.22-3.30 nmol/L"),
            ("Thyroid Stimulating Hormone (TSH)", "IU/ml", "", "0.30-5.00 IU/ml"),
            ("Titre", "", "", ""),
            ("Total Thyroxine (T4)", "µg/dl", "", "5.10 - 14.10 µg/dl"),
            ("Total Tri-iodothyronine (T3)", "ng/ml", "", "0.8-2.0 ng/ml"),
            ("Troponin-I", "ng/ml", "", "Normal: 0.00-0.04 ng/ml"),
            ("Tuberculin Test", "mm", "", ""),
            ("Cytomorphology with normal", "", "", ""),
            ("Absent", "", "", ""),
            ("Acidic", "", "", ""),
            ("Actively Motile", "", "", ""),
            ("Alkaline", "", "", ""),
            ("%of Sperm Abnormality", "", "", ""),
            ("Body", "", "", ">30% Abnormal"),
            ("Other Cells", "", "", ""),
            ("Color", "", "", ""),
            ("Completely Liquefied", "", "", ""),
            ("Feebly Motile", "", "", ""),
            ("Fructose", "", "", ""),
            ("Head", "", "", ">30% Abnormal"),
            ("Leukocytes", "/HPF", "", ""),
            ("Epithelial Cells", "", "", ""),
            ("RBC Germ Cells", "", "", ""),
            ("Incompletely Liquefied", "", "", ""),
            ("Liquefaction", "", "", ""),
            ("Non Motile", "", "", ""),
            ("Opinion", "", "", ""),
            ("PH", "", "", ""),
            
            ("Present", "", "", ""),
            ("Prostatic Smear for Gram Staining", "", "", ""),
            ("Pus for AFB", "", "", ""),
            ("Pus for Gram Staining", "", "", ""),
            ("Skin / Nail Scraping for fungus", "", "", ""),
            ("Sperm Clumping", "", "", ""),
            ("Sperm Count", "Millions/ml", "", "40-120 Millions/ml"),
            ("Sperm Morphology", "", "", ""),
            ("Sperm Motility", "", "", ""),
            ("Sperm Viability", "", "", ""),
            ("Sputum for AFB", "", "", ""),
            ("Sputum for Eosinophil", "", "", ""),
            ("Sputum for Gram Staining", "", "", ""),
            ("Tail", "", "", ">30% Abnormal"),
            ("Urethral Discharge for Gram-staining", "", "", ""),
            ("Urethral for Gram Staining", "", "", ""),
            ("Volume", "", "", ""),
            ("Organised Deposits", "", "", ""),
            ("Unorganised Deposits", "", "", ""),
            ("Amorphous Phosphate", "", "", ""),
            ("Bacteria", "", "", ""),
            ("Calcium Oxalate", "", "", ""),
            ("Casts", "", "", ""),
            ("Cells", "", "", ""),
            ("Crystal of", "", "", ""),
            ("Cyst", "", "", ""),
            ("Epithelial Cast", "", "", ""),
            ("Epithelial Cells", "", "", ""),
            ("Fat Globules", "", "", ""),
            ("Fungus", "", "", ""),
            ("Granular Cast", "", "", ""),
            ("Hyaline Cast", "", "", ""),
            ("Larva of", "", "", ""),
            ("Macrophage", "", "", ""),
            ("Others", "", "", ""),
            ("Ova of", "", "", ""),
            ("Parasite", "", "", ""),
            ("Pus Cell", "", "", ""),
            ("Pus Cell cast", "", "", ""),
            ("Pus Cells", "", "", ""),
            ("R.B.C.", "", "", ""),
            ("R.B.C. cast", "", "", ""),
            ("RBC cast", "", "", ""),
            ("Spermatozoa", "", "", ""),
            ("Sulphonamide crystal", "", "", ""),
            ("Tripple Phosphate", "", "", ""),
            ("Trichomonas", "", "", ""),
            ("Urates", "", "", ""),
            ("Uric Acid crystal", "", "", ""),
            ("Vegetable Cell", "", "", ""),
            ("IgG", "", "", ""),
            ("ICT for Dengue Antibody: IgM", "", "", ""),
            ("Pregnancy Test", "", "", ""),
            ("Urinary Protein", "", "", ""),
            ("Urine for A.F.B (3 sample)", "", "", ""),
            ("Urine for Amylase", "u/L", "", "1000 u/L"),
            ("Urine for Bence-Jone's Protein", "", "", ""),
            ("Urine for Bile Pigment", "", "", ""),
            ("Urine for Bile Salt", "", "", ""),
            ("Urine for Haemoglobin", "", "", ""),
            ("Urine for Ketone Bodies", "", "", ""),
            ("Urine for Specific Gravity", "", "", ""),
            ("Appearance", "", "", ""),
            ("Blood", "", "", ""),
            ("Color", "", "", ""),
            ("Consistency", "", "", ""),
            ("Helminths", "", "", ""),
            ("Mucous", "", "", ""),
            ("Quantity", "", "", ""),
            ("Sediment", "", "", ""),
            ("Specific Gravity", "", "", ""),
            ("Bicarbonate", "mmol/L", "", "Upto 23-29 mmol/L"),
            ("Chloride", "mmol/L", "", "Upto 95-107 mmol/L"),
            ("Potassium", "mmol/L", "", "Upto 3.5-5.5 mmol/L"),
            ("Sodium", "mmol/L", "", "Upto 135-148 mmol/L"),
            ("Comments", "", "", ""),
            ("Vidal Test", "", "", ""),
            ("A.S.O Titre", "IU/ml", "", "Upto 200 IU/ml"),
            ("Activated Partial Thromboplastin", "", "", ""),
            ("Aldehyde Test", "", "", ""),
            ("Anti HIV", "", "", ""),
            ("Anti-HCV", "", "", ""),
            ("C-Reactive Protein (CRP)", "mg/L", "", "0.01 - 5.00 mg/L"),
            ("Control", "Second", "", ""),
            ("Dengue Ag NS1", "", "", ""),
            ("Dengue Antibody IgG, IgM", "", "", ""),
            ("Febrile Antigen", "", "", ""),
            ("HBeAg", "", "", ""),
            ("HBs Ag", "", "", ""),
            ("HBs Ag (Screening)", "", "", ""),
            ("HIV (AIDS) by ICT", "", "", ""),
            ("ICT for Filaria", "", "", ""),
            ("ICT for Kala-Azar", "", "", ""),
            
            ("ICT for Malaria", "", "", ""),
            ("ICT for Tuberculosis", "", "", ""),
            ("Patient", "", "", "Second"),
            ("R.A. Test", "", "", ""),
            ("Salmonella Paratyphi-AH (AH)", "", "", "Titre Upto 1:80 each"),
            ("Salmonella Paratyphi-AO (AO)", "", "", "Titre Upto 1:80 each"),
            ("Salmonella Paratyphi-BH (BH)", "", "", "Titre Upto 1:80 each"),
            ("Salmonella Paratyphi-BO (BO)", "", "", "Titre Upto 1:80 each"),
            ("Salmonella Typhi-H (TH)", "", "", "Titre Upto 1:80 each"),
            ("Salmonella Typhi-O (TO)", "", "", "Titre Upto 1:80 each"),
            ("TPHA", "", "", ""),
            ("Urine for hCG (Pregnancy Test)", "", "", ""),
            ("V.D.R.L (Qualitative/Quantitative)", "", "", ""),
            ("Stool for Reducing Substances", "", "", ""),
            ("24 hrs. urinary total protein", "gm/24hrs", "gm", ""),
            ("24 hrs. urine volume", "ml", "", ""),
            ("Albumin", "", "", ""),
            ("Glucose", "", "", ""),
            ("Protein", "", "", ""),
            ("Ratio", "", "", ""),
            ("Urinary total protein", "", "", ""),
            ("Urine Amylase", "U/L", "", "1000 U/L"),
            ("Urine for A.F.B.", "", "", ""),
            ("Urine for Micro Albumin", "", "", ""),
            ("Urine for Albumin", "", "", ""),
            ("Urine for Creatinine", "", "", ""),
            ("Urine for PH", "", "", ""),
            ("Urine for Reducing Substance", "", "", ""),
            ("Urine for Suger", "", "", ""),
            ("Urine Specific Gravity", "", "", ""),
            ("Urine Volume", "", "", ""),
            ("Urine for Ketone Bodies", "", "", ""),
        ]

        for name,unit,unit2,reference_range in test_items_data:
            TestItem.objects.create(
                name=name,
                unit=unit,
                unit2=unit2,
                reference_range=reference_range,
                created_by=admin_user,
                updated_by=admin_user
            )

    def setup_bed_types(self):
        types = [
            ("General", "GEN", 500.00),
            ("Cabin", "CAB", 1200.00),
            ("ICU", "ICU", 2500.00),
            ("NICU", "NICU", 3000.00),
            ("Deluxe", "DLX", 1800.00),
        ]
        for name, code, rate in types:
            BedType.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "daily_rate": rate,
                    "description": f"{name} bed with standard facilities"
                }
            )
        self.stdout.write(self.style.SUCCESS("🛏️ Bed Types যুক্ত ✅"))

    def setup_payment_methods(self):
        methods = [
            ("cash", "Cash", 0),
            ("card", "Card", 0),
            ("mobile", "Mobile Payment", 1.5),
            ("bank", "Bank Transfer", 0),
        ]
        for code, name, surcharge in methods:
            PaymentMethodType.objects.get_or_create(
                code=code,
                defaults={"name": name, "surcharge_percent": surcharge}
            )
        self.stdout.write(self.style.SUCCESS("💳 Payment Methods যুক্ত ✅"))

    def setup_consultants(self):
        consultant = [
            ("Prof. Dr. BD Bidhu", "external", "Medicine", "Rangpur Medical", "01700000001"),
            ("Prof. Dr. Md. Mahfuzer Rahman MBBS, MD (Medicine), FACP (USA), FRCP (Edin, UK), FRCP (Glasgow, UK)", "external", "Medicine", "Rangpur Medical", "01700000004"),            
            ("Prof. Dr. Ranjit Basak MBBS, FCPS (Pediatrics), Newborn, Child Diseases & Nutrition Specialist", "external", "Pediatrics", "City Hospital", "01700000002"),
            ("Dr. Kamal Uddin", "referrer", "General", "Private Clinic", "01700000003"),
        ]
        admin = CustomUser.objects.filter(username="admin").first()
        for name, ctype, spec, org, contact in consultant:
            Consultant.objects.get_or_create(
                name=name,
                type=ctype,
                defaults={
                    "specialization": spec,
                    "organization": org,
                    "contact": contact,
                    "created_by": admin,
                    "updated_by": admin,
                    "created_at": timezone.now(),
                    "updated_at": timezone.now()
                }
            )
        self.stdout.write(self.style.SUCCESS("👨‍⚕️ Consultant প্রোফাইল যুক্ত ✅"))

    def setup_test_accessories(self):
        accessories = [
            ("Vaccuam Needle", 20),
            ("Vacuette Red", 20),
            ("Vacuette EDTA", 20),
            ("Black Tube", 25),
            ("U.S Pot", 10),
            ("C/S Pot", 10),
            ("Vacuette PT", 20),
        ]

        for name, price in accessories:
            obj, created = TestAccessory.objects.get_or_create(
                name=name,
                defaults={
                    'price': price,
                    'description': '',
                    'created_by': None,
                    'updated_by': None,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ TestAccessory তৈরি হয়েছে: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ TestAccessory আগে থেকেই আছে: {name}"))