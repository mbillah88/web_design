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
            ("ECHO", "Radiology", "হৃদপিণ্ডের আল্ট্রাসাউন্ড"),
            ("ECG", "Radiology", "হৃদপিণ্ডের আল্ট্রাসাউন্ড"),
            ("CT Scan", "Radiology", "কম্পিউটারাইজড টোমোগ্রাফি"),
            ("MRI", "Radiology", "ম্যাগনেটিক রেজোন্যান্স ইমেজিং"),
            ("Mammography", "Radiology", "স্তন ক্যান্সার স্ক্রিনিং"),
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
        groups = [
            ("1 hrs After Lunch", "Biochemical", 120, 108, 10),
            ("2 hrs After Lunch", "Biochemical", 120, 108, 10),
            ("1 hrs After 75 gm glucose", "Biochemical", 120, 108, 10),
            ("2 hrs After 75 gm glucose", "Biochemical", 120, 108, 10),
            ("1 hrs After Breakfast", "Biochemical", 120, 108, 10),
            ("2 hrs After Breakfast", "Biochemical", 120, 108, 10),
            ("1 hrs After Dinner", "Biochemical", 120, 108, 10),
            ("2 hrs After Dinner", "Biochemical", 120, 108, 10),
            ("1 hrs After Iftar", "Biochemical", 120, 108, 10),
            ("2 hrs After Iftar", "Biochemical", 120, 108, 10),
            ("After Dinner", "Biochemical", 120, 108, 10),
            ("After Lunch", "Biochemical", 120, 108, 10),
            ("RBS with CUS", "Biochemical", 120, 108, 10),
            ("Before Iftar", "Biochemical", 120, 108, 10),
            ("Before Lunch", "Biochemical", 120, 108, 10),
            ("Mid Day", "Biochemical", 120, 108, 10),
            ("Fasting Lipid Profile (Four Test)", "Biochemical", 1000, 900, 10),
            ("Random Lipid Profile (Four Test)", "Biochemical", 1000, 900, 10),
            ("FBS (Fasting Blood Sugar)", "Biochemical", 120, 108, 10),
            ("ACR", "Biochemical", 1000, 900, 10),
            ("ACTH", "Biochemical", 1030, 927, 10),
            ("Alkaline Phosphatase", "Biochemical", 400, 360, 10),
            ("Alpha Feto Protein", "Biochemical", 1000, 900, 10),
            ("ANA Test", "Biochemical", 1200, 1080, 10),
            ("ANF", "Biochemical", 800, 720, 10),
            ("Anti Phospolied  Ab IgG,IgM", "Biochemical", 3000, 2700, 10),
            ("Anti Cardiolipin AB IgG,IgM", "Biochemical", 3000, 2700, 10),
            ("Anti Cardiolipin IgA,IgG,IgM", "Biochemical", 3000, 2700, 10),
            ("Anti CCP", "Biochemical", 2000, 1800, 10),
            ("Anti DNA(ELISA)", "Biochemical", 1000, 900, 10),
            ("Anti DS DNA", "Biochemical", 800, 720, 10),
            ("Anti HBc", "Biochemical", 900, 810, 10),
            ("Anti HBc IgG", "Biochemical", 1200, 1080, 10),
            ("Anti HCV", "Biochemical", 850, 765, 10),
            ("Anti HIV", "Biochemical", 1000, 900, 10),
            ("Anti Scl - 70", "Biochemical", 2500, 2250, 10),
            ("APTT", "Biochemical", 800, 720, 10),
            ("Blood For LDH", "Biochemical", 1000, 900, 10),
            ("Blood Urea", "Biochemical", 250, 225, 10),
            ("C ANCA", "Biochemical", 1500, 1350, 10),
            ("C-Peptide (Fasting)", "Biochemical", 1700, 1530, 10),
            ("CPK", "Biochemical", 1000, 900, 10),
            ("CSF for ADA", "Biochemical", 1300, 1170, 10),
            ("CSF for Biochemestry, Cytology & Microbiology", "Biochemical", 1200, 1080, 10),
            ("D-Dimer", "Biochemical", 1500, 1350, 10),
            ("Dangue IGG IGM(Dangue Special Pack)", "Biochemical", 500, 450, 10),
            ("Estimation of testostoren", "Biochemical", 850, 765, 10),
            ("FT3 (ELISA)", "Biochemical", 900, 810, 10),
            ("FT4 (ELISA)", "Biochemical", 1000, 900, 10),
            ("TSH (ELISA)", "Biochemical", 160, 144, 10),
            ("FSH (ELISA)", "Biochemical", 900, 810, 10),
            ("Growth Hormone", "Biochemical", 600, 540, 10),
            ("HBA1C", "Biochemical", 1000, 900, 10),
            ("HBV DNA (PCR)", "Biochemical", 8000, 7200, 10),
            ("Hbs Ag (ELISA)", "Biochemical", 800, 720, 10),
            ("Hbs-Ag (Confirmatory)", "Biochemical", 500, 450, 10),
            ("ICT For Dangue Antibody(Igm & IgG)", "Biochemical", 1000, 900, 10),
            ("ICT For Dangue(IgM & igG)", "Biochemical", 1000, 900, 10),
            ("INR", "Biochemical", 1000, 900, 10),
            ("Insulin Level (Fasting)", "Biochemical", 2000, 1800, 10),
            ("LFT(S.Bilirubin+S.Alk.Phosphatase+SGPT+SGOT)", "Biochemical", 1000, 900, 10),
            ("NT. Pro BNP", "Biochemical", 2500, 2250, 10),
            ("Oestrogen/Estrogen", "Biochemical", 1000, 900, 10),
            ("Outsample (Blood) Collection Fee", "Biochemical", 200, 180, 10),
            ("P ANCA", "Biochemical", 1500, 1350, 10),
            ("Progesterone", "Biochemical", 1000, 900, 10),
            ("PSA (ELISA)", "Biochemical", 1000, 900, 10),
            ("RFT (S.Creatinine+S.Urea)", "Biochemical", 900, 810, 10),
            ("Rubella IgG", "Biochemical", 850, 765, 10),
            ("S. Tg Level (Thyroglobulin)", "Biochemical", 2000, 1800, 10),
            ("S. eGFR (Estimated Glomerular Filtration Rate)", "Biochemical", 1200, 1080, 10),
            ("S.AC 19-9", "Biochemical", 1000, 900, 10),
            ("S.Albumin", "Biochemical", 400, 360, 10),
            ("S.Amylase", "Biochemical", 1000, 900, 10),
            ("S.Bilirubin  ( Direct)", "Biochemical", 500, 450, 10),
            ("S.Bilirubin (Indirect+Total+Direct)", "Biochemical", 800, 720, 10),
            ("S.Bilirubin (Total)", "Biochemical", 200, 180, 10),
            ("S.Bilirubin Indirect.", "Biochemical", 400, 360, 10),
            ("S.C3 Level", "Biochemical", 1000, 900, 10),
            ("S.CA 15-3", "Biochemical", 1000, 900, 10),
            ("S.Ca 19-9", "Biochemical", 1000, 900, 10),
            ("S.Calcium", "Biochemical", 400, 360, 10),
            ("S.Ceruloplasmin Level", "Biochemical", 1500, 1350, 10),
            ("S.Cholesterol", "Biochemical", 250, 225, 10),
            ("S.Cortisol (AM)", "Biochemical", 1000, 900, 10),
            ("S.Cortisol (PM)", "Biochemical", 1000, 900, 10),
            ("S.Creatinine", "Biochemical", 400, 360, 10),
            ("S.Electrolyte", "Biochemical", 1000, 900, 10),
            ("S.Ferritin", "Biochemical", 1200, 1080, 10),
            ("S.IgE", "Biochemical", 1000, 900, 10),
            ("S.Iron", "Biochemical", 800, 720, 10),
            ("S.Iron Profile", "Biochemical", 2800, 2520, 10),
            ("S.LDH", "Biochemical", 700, 630, 10),
            ("S.LH", "Biochemical", 1000, 900, 10),
            ("S.Lipase", "Biochemical", 1000, 900, 10),
            ("S.Phosphate", "Biochemical", 1000, 900, 10),
            ("S.Protein Electrophoresis", "Biochemical", 2000, 1800, 10),
            ("S.Total Protein", "Biochemical", 350, 315, 10),
            ("S.TIBC", "Biochemical", 600, 540, 10),
            ("S.Triglyceride", "Biochemical", 350, 315, 10),
            ("S.Urea", "Biochemical", 220, 198, 10),
            ("S.Uric Acid", "Biochemical", 400, 360, 10),
            ("Spot PCR (Protin Creatinen Ratio)", "Biochemical", 450, 405, 10),
            ("Thyroid Anti Body", "Biochemical", 2000, 1800, 10),
            ("TORCH IgM/IgG (10 Test)", "Biochemical", 8000, 7200, 10),
            ("TPHA", "Biochemical", 700, 630, 10),
            ("Troponin I", "Biochemical", 1000, 900, 10),
            ("TORCH IgM/IgG (10 Test)", "Biochemical", 8000, 7200, 10),
            ("TPHA", "Biochemical", 700, 630, 10),
            ("Troponin I", "Biochemical", 1000, 900, 10),
            ("Tryglyceride (TG)", "Biochemical", 300, 270, 10),
            ("Urine For C/S", "Biochemical", 640, 576, 10),
            ("Urine R/E", "Biochemical", 250, 225, 10),
            ("Urine for Copper", "Biochemical", 1350, 1215, 10),
            ("UTP (Urinary total protein)", "Biochemical", 1000, 900, 10),
            ("blood c/s", "Biochemical", 1000, 900, 10),
            ("s.copper", "Biochemical", 2500, 2250, 10),
            ("S.IGG", "Biochemical", 1000, 900, 10),
            ("urine for Phosphates", "Biochemical", 600, 540, 10),
        ]

        groups += [
            ("AMH (Anti- Mullerian Hormone)", "Haematological", 3000, 2700, 10),
            ("MCHC", "Haematological", 330, 297, 10),
            ("Blood For MP", "Haematological", 1200, 1080, 10),
            ("Hb %", "Haematological", 250, 225, 10),
            ("Anti HBs", "Haematological", 1000, 900, 10),
            ("PBF (Peripheral Blood Film Study)", "Haematological", 500, 450, 10),
            ("BT,CT", "Haematological", 300, 270, 10),
            ("Prolactein", "Haematological", 1200, 1080, 10),
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
        ]
        groups += [
            ("Anti Hbe (Elisa)", "Serological", 1200, 1080, 10),
            ("Anty HCV (Screening)", "Serological", 1200, 1080, 10),
            ("Anti H-Pylori IgG", "Serological", 1000, 900, 10),
            ("S.IGM", "Serological", 1200, 1080, 10),
            ("HLA B-27", "Serological", 4000, 3600, 10),
            ("Triple Antigen", "Serological", 1100, 990, 10),
            ("HCV RNA", "Serological", 10000, 9000, 10),
            ("Rh-antibody titre", "Serological", 1000, 900, 10),
            ("Urine for ketonbody", "Serological", 400, 360, 10),
            ("T.P.H.A.", "Serological", 800, 720, 10),
            ("S.Folic Acid", "Serological", 2000, 1800, 10),
            ("Urine for PCR", "Serological", 800, 720, 10),
            ("S.Albumin Ratio (Next)", "Serological", 125, 113, 10),
            ("Rubella (IgM)", "Serological", 1200, 1080, 10),
            ("Prostatic smear for Gram stainnig", "Serological", 600, 540, 10),
            ("Urine For Pregnency", "Serological", 250, 225, 10),
            ("P/S For R/E", "Serological", 240, 216, 10),
            ("Urinary Amylase", "Serological", 600, 540, 10),
            ("Anti RNP Antibody", "Serological", 2500, 2250, 10),
            ("Seram Toxoplasma Elaisa", "Serological", 1000, 900, 10),
            ("H.Pylori (IgG,IgM)", "Serological", 2000, 1800, 10),
            ("ICT-Filaria", "Serological", 1200, 1080, 10),
            ("VDRL (Qualitive)", "Serological", 500, 450, 10),
            ("VDRL (Quantitive)", "Serological", 500, 450, 10),
            ("ICT -TB", "Serological", 1000, 900, 10),
            ("ICT For Malaria", "Serological", 1200, 1080, 10),
            ("Vit B12", "Serological", 2500, 2250, 10),
            ("Widal Test", "Serological", 500, 450, 10),
            ("CRP (Govt fixed rate)", "Serological", 600, 600, 0),
            ("HCV (Antibody)", "Serological", 850, 765, 10),
            ("Anti HBe Ag", "Serological", 1000, 900, 10),
            ("Urine For Electrolyte", "Serological", 1600, 1440, 10),
            ("S. Lactate", "Serological", 1600, 1440, 10),
            ("CA 19.9", "Serological", 1200, 1080, 10),
            ("Hbs Ag (Screening)", "Serological", 500, 450, 10),
            ("Sputum For A.F.B. 2 SAMPLE", "Serological", 1200, 1080, 10),
            ("Urine For Albumin", "Serological", 300, 270, 10),
            ("Screening & Crossmatch", "Serological", 1000, 1000, 0),
            ("Hb-Electrophoresis", "Serological", 1500, 1350, 10),
            ("HBe Ag", "Serological", 1200, 1080, 10),
            ("Anti HAV", "Serological", 1200, 1080, 10),
            ("Dengue NS1 (Govt fixed rate)", "Serological", 300, 300, 0),
            ("S.Lithium", "Serological", 1000, 900, 10),
            ("Urine For bence-jones Protein", "Serological", 250, 225, 10),
            ("Urine for ACR", "Serological", 1200, 1080, 10),
            ("FNAC", "Serological", 1500, 1350, 10),
            ("Fluid For C/S", "Serological", 800, 720, 10),
            ("Toxoplasma Gondi (IgG)", "Serological", 1000, 900, 10),
            ("Triple/Febrile Antizen", "Serological", 1100, 990, 10),
            ("CSF Analysis", "Serological", 1200, 1200, 0),
            ("CFT For Filaria", "Serological", 650, 585, 10),
            ("Blood Grouping", "Serological", 150, 135, 10),
            ("ASO Titre", "Serological", 500, 450, 10),
            ("Ascitic Fluid  Analysis", "Serological", 2500, 2250, 10),
            ("Sputam for Eosinophil", "Serological", 200, 180, 10),
            ("Dengue Panel", "Serological", 1200, 1080, 10),
            ("TORCH Panel", "Serological", 3000, 2700, 10),
        ]
        groups += [
            ("C4", "Cytological", 1200, 1080, 10),
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
            ("Biopsy (Large) - (The Lab)", "Cytological", 4250, 4250, 0),
        ]
        groups += [
            ("ICT FOR Kala zar", "Microbiological", 1200, 1080, 10),
            ("Anti mitochondrial antibody", "Microbiological", 3000, 2700, 10),
            ("Sputam for afb", "Microbiological", 600, 540, 10),
            ("Anti HEV IgM", "Microbiological", 1200, 1080, 10),
            ("Toxoplasma Gondi (IgM)", "Microbiological", 1000, 900, 10),
            ("Gram Staining", "Microbiological", 350, 315, 10),
            ("MT Test (Tuberculin Test)", "Microbiological", 350, 315, 10),
            ("Nail Scraping for fungus", "Microbiological", 250, 225, 10),
            ("Pus for C/S", "Microbiological", 1000, 900, 10),
            ("Sputum  For Malignancy", "Microbiological", 500, 450, 10),
            ("Sputum for AFB 3 Sample", "Microbiological", 1800, 1620, 10),
            ("Swab for c/s", "Microbiological", 800, 720, 10),
            ("Stool for OBT", "Microbiological", 400, 360, 10),
            ("Stool for Reducing Substance", "Microbiological", 100, 90, 10),
            ("Urine for chyle", "Microbiological", 800, 800, 0),
            ("Skin Scraping for Fungus", "Microbiological", 250, 225, 10),
            ("Semen Analysis", "Microbiological", 700, 630, 10),
            ("Sputam C/S", "Microbiological", 800, 720, 10),
            ("Anti smooth muscle antibody", "Microbiological", 4000, 3600, 10),
            ("Anti liver kidney microsomal antibody", "Microbiological", 3200, 2880, 10),
            ("Stool R/E", "Microbiological", 300, 270, 10),
        ]
        groups += [
            ("Anti Thyroid Antibody (Anti TPO + Anti TG)", "Immunological", 2400, 2160, 10),
            ("Blood Grouping and Cross Matching", "Immunological", 1000, 1000, 0),
            ("CA-125", "Immunological", 1200, 1080, 10),
            ("PTH (Para Thyroid Hormone)", "Immunological", 1500, 1350, 10),
            ("25 (OH) Vitamin D", "Immunological", 3000, 2700, 10),
            ("PTH", "Immunological", 1500, 1350, 10),
            ("Beta-hCG", "Immunological", 1200, 1080, 10),
            ("Anti Hbs Ag Titre", "Immunological", 1200, 1080, 10), 
            ("Anti-acetylcholine receptor (AChR)", "Immunological", 3570, 3213, 10), 
            ("Anti- Muscle-Kinase(Anti MuSK)", "Immunological", 3500, 3150, 10), 
            ("ENA Profile", "Immunological", 8000, 7200, 10), 
            ("Blood Coomb's test", "Immunological", 1500, 1350, 10), 
            ("Anti Hbc IgM", "Immunological", 1200, 1080, 10),
            ("Anti TPO", "Immunological", 1200, 1080, 10), 
            ("Anti TG", "Immunological", 1200, 1080, 10),
        ]
        groups += [
            ("S.Oestrogen / Estradiol / Estrogen", "Hormone", 1200, 1080, 10),
            ("C3", "Hormone", 1200, 1080, 10),
            ("S.Magnesium", "Hormone", 1200, 1080, 10),
            ("S.Copper", "Hormone", 2500, 2250, 10),
        ]
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
        groups += [
            ("ECG in All Leads. Digital", "ECG", 350, 315, 10),
            ("CTG", "ECHO", 1000, 900, 10),
            ("Echo Cardiogram (2D & M-Mode)", "ECHO", 1200, 1080, 10),
            ("Echo Cardiogram Color Doppler", "ECHO", 2300, 2070, 10),
        ]
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
            ("Foot Lataral view (Lt) - X- Ray", "Digital X-Ray", 400, 360, 10),

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
       
        #1 hrs After Breakfast and Corresponding Urine Sugar
        items = [
            ("1 hrs After Breakfast (Blood Sugar)", "1 hrs After Breakfast", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "1 hrs After Breakfast", "Result", "Nil/Trace"),
        ]
        #2 hrs After Breakfast (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("2 hrs After Breakfast (Blood Sugar)", "2 hrs After Breakfast", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "2 hrs After Breakfast", "Result", "Nil/Trace"),
        ]
        #1 hrs After Dinner (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("1 hrs After Dinner (Blood Sugar)", "1 hrs After Dinner", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "1 hrs After Dinner", "Result", "Nil/Trace"),
        ]
        #2 hrs After Dinner (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("2 hrs After Dinner (Blood Sugar)", "2 hrs After Dinner", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "2 hrs After Dinner", "Result", "Nil/Trace"),
        ]
        #1 hrs After Lunch (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("1 hrs After Lunch (Blood Sugar)", "1 hrs After Lunch", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "1 hrs After Lunch", "Result", "Nil/Trace"),
        ]
        #2 hrs After Lunch (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("2 hrs After Lunch (Blood Sugar)", "2 hrs After Lunch", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "2 hrs After Lunch", "Result", "Nil/Trace"),
        ]
        #1 hr After 75 gm glucose
        items += [
            ("1 hr After 75 gm glucose (Blood)", "1 hrs After 75 gm glucose", "mmol/L", "<10.0"),
            ("Corresponding Urine Sugar", "1 hrs After 75 gm glucose", "Result", "Nil/Trace"),
        ]
        #2 hrs After 75 gm glucose
        items += [
            ("2 hrs After 75 gm glucose (Blood)", "2 hrs After 75 gm glucose", "mmol/L", "<7.8"),
            ("Corresponding Urine Sugar", "2 hrs After 75 gm glucose", "Result", "Nil/Trace"),
        ]
        #Before Lunch (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("Before Lunch (Blood Sugar)", "Before Lunch", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "Before Lunch", "Result", "Nil/Trace"),
        ]
        #After Lunch (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("After Lunch (Blood Sugar)", "After Lunch", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "After Lunch", "Result", "Nil/Trace"),
        ]
        #Before Dinner (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("Before Dinner (Blood Sugar)", "Before Dinner", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "Before Dinner", "Result", "Nil/Trace"),
        ]
        #After Dinner (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("After Dinner (Blood Sugar)", "After Dinner", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "After Dinner", "Result", "Nil/Trace"),
        ]
        #Before Iftar (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("Before Iftar (Blood Sugar)", "Before Iftar", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "Before Iftar", "Result", "Nil/Trace"),
        ]
        #1 hr After Iftar (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("1 hr After Iftar (Blood Sugar)", "1 hrs After Iftar", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "1 hrs After Iftar", "Result", "Nil/Trace"),
        ]
        #2 hrs After Iftar (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("2 hrs After Iftar (Blood Sugar)", "2 hrs After Iftar", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "2 hrs After Iftar", "Result", "Nil/Trace"),
        ]
        #Mid Day (Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("Mid Day (Blood Sugar)", "Mid Day", "mmol/L", "4.4–7.8"),
            ("Corresponding Urine Sugar", "Mid Day", "Result", "Nil/Trace"),
        ]
        #🧪FBS (Fasting Blood Sugar) and Corresponding Urine Sugar
        items += [
            ("Fasting Blood Sugar", "FBS (Fasting Blood Sugar)", "mmol/L", "3.9–5.5"),
            ("Corresponding Urine Sugar", "FBS (Fasting Blood Sugar)", "Result", "Nil/Trace"),
        ]
        #🧪FBS with CUS and Corresponding Urine Sugar
        items += [
            ("Fasting Blood Sugar", "FBS with CUS", "mmol/L", "3.9–5.5"),
            ("Corresponding Urine Sugar", "FBS with CUS", "Result", "Nil/Trace"),
        ]
        #🧪RBS with CUS and Corresponding Urine Sugar
        items += [
            ("Fasting Blood Sugar", "RBS with CUS", "mmol/L", "3.9–5.5"),
            ("Corresponding Urine Sugar", "RBS with CUS", "Result", "Nil/Trace"),
        ]

        #🧪Random Lipid Profile (Four Test)
        items += [
            ("Total Cholesterol", "Fasting Lipid Profile (Four Test)", "mg/dL", "<200"),
            ("HDL Cholesterol", "Fasting Lipid Profile (Four Test)", "mg/dL", ">40"),
            ("LDL Cholesterol", "Fasting Lipid Profile (Four Test)", "mg/dL", "<100"),
            ("Triglyceride", "Fasting Lipid Profile (Four Test)", "mg/dL", "<150"),
        ]
       
        # #🧪 GTT (3 Samples)
        # items += [
        #     ("Fasting Glucose", "GTT (3 Samples)", "mmol/L", "<5.6"),
        #     ("1 Hour Glucose", "GTT (3 Samples)", "mmol/L", "<10.0"),
        #     ("2 Hour Glucose", "GTT (3 Samples)", "mmol/L", "<7.8"),
        #     ("Corresponding Urine Sugar", "GTT (3 Samples)", "Result", "Nil/Trace"),
        # ]

        #🧪 GTT (5 Samples)
        items += [
            ("Fasting Glucose", "GTT (5 Samples)", "mmol/L", "<5.6"),
            ("0.5 Hour Glucose", "GTT (5 Samples)", "mmol/L", "<9.0"),
            ("1 Hour Glucose", "GTT (5 Samples)", "mmol/L", "<10.0"),
            ("1.5 Hour Glucose", "GTT (5 Samples)", "mmol/L", "<9.0"),
            ("2 Hour Glucose", "GTT (5 Samples)", "mmol/L", "<7.8"),
            ("Corresponding Urine Sugar", "GTT (5 Samples)", "Result", "Nil/Trace"),
        ]

        #🧪 CBC (Complete Blood Count)
        items += [
            ("Hemoglobin", "CBC (Complete Blood Count)", "g/dL", "13.5–17.5"),
            ("WBC Count", "CBC (Complete Blood Count)", "x10^3/µL", "4.0–11.0"),
            ("RBC Count", "CBC (Complete Blood Count)", "x10^6/µL", "4.5–6.0"),
            ("Hematocrit", "CBC (Complete Blood Count)", "%", "40–50"),
            ("MCV", "CBC (Complete Blood Count)", "fL", "80–100"),
            ("MCH", "CBC (Complete Blood Count)", "pg", "27–33"),
            ("MCHC", "CBC (Complete Blood Count)", "g/dL", "32–36"),
            ("Platelet Count", "CBC (Complete Blood Count)", "x10^3/µL", "150–450"),
            ("Differential Count", "CBC (Complete Blood Count)", "%", "Neut 40–75, Lymph 20–45"),
            ("ESR", "CBC (Complete Blood Count)", "mm/hr", "Male: <15, Female: <20"),
        ]

        #🧪 TC, DC, ESR
        items += [
            ("Total Count (TC)", "TC,DC,ESR", "x10^3/µL", "4.0–11.0"),
            ("Differential Count (DC)", "TC,DC,ESR", "%", "Neut 40–75, Lymph 20–45"),
            ("ESR", "TC,DC,ESR", "mm/hr", "Male: <15, Female: <20"),
        ]
        #🧪 BT, CT
        items += [
            ("Bleeding Time (BT)", "BT,CT", "minutes", "2–7"),
            ("Clotting Time (CT)", "BT,CT", "minutes", "3–10"),
        ]
       
        #🧪 Liver Function Test (LFT)
        items += [
            ("Total Bilirubin", "Liver Function Test (LFT)", "mg/dL", "0.3–1.2"),
            ("Direct Bilirubin", "Liver Function Test (LFT)", "mg/dL", "<0.3"),
            ("SGPT (ALT)", "Liver Function Test (LFT)", "U/L", "7–56"),
            ("SGOT (AST)", "Liver Function Test (LFT)", "U/L", "10–40"),
            ("Alkaline Phosphatase", "Liver Function Test (LFT)", "U/L", "44–147"),
            ("Total Protein", "Liver Function Test (LFT)", "g/dL", "6.0–8.3"),
            ("Albumin", "Liver Function Test (LFT)", "g/dL", "3.5–5.0"),
            ("Globulin", "Liver Function Test (LFT)", "g/dL", "2.0–3.5"),
            ("A/G Ratio", "Liver Function Test (LFT)", "Ratio", "1.0–2.2"),
        ]
        #🧠 Thyroid Profile (T3, T4, TSH)   
        items += [
            ("TSH", "Thyroid Profile (T3, T4, TSH)", "µIU/mL", "0.4–4.0"),
            ("Free T3 (FT3)", "Thyroid Profile (T3, T4, TSH)", "pg/mL", "2.0–4.4"),
            ("Free T4 (FT4)", "Thyroid Profile (T3, T4, TSH)", "ng/dL", "0.93–1.7"),
        ]
        #🧠 Renal Profile (Kidney Function Test)
        items += [
            ("Serum Creatinine", "Renal Profile", "mg/dL", "0.6–1.3"),
            ("Blood Urea", "Renal Profile", "mg/dL", "10–50"),
            ("Uric Acid", "Renal Profile", "mg/dL", "3.5–7.2"),
            ("eGFR", "Renal Profile", "mL/min/1.73m²", ">90"),
            ("Sodium (Na+)", "Renal Profile", "mmol/L", "135–145"),
            ("Potassium (K+)", "Renal Profile", "mmol/L", "3.5–5.1"),
            ("Chloride (Cl−)", "Renal Profile", "mmol/L", "98–107"),
        ]
        #🦠 Dengue Panel
        items += [
            ("Dengue NS1 Antigen", "Dengue Panel", "Result", "Negative"),
            ("Dengue IgM", "Dengue Panel", "Result", "Negative"),
            ("Dengue IgG", "Dengue Panel", "Result", "Negative"),
            ("Platelet Count", "Dengue Panel", "x10^3/µL", "150–450"),
            ("Hematocrit", "Dengue Panel", "%", "40–50"),
        ]
        #🧠 Hepatitis Panel
        items += [
            ("HBsAg", "Hepatitis Panel", "IU/mL", "Negative"),
            ("Anti-HBs", "Hepatitis Panel", "IU/L", ">10"),
            ("Anti-HBc", "Hepatitis Panel", "IU/mL", "Negative"),
            ("HBeAg", "Hepatitis Panel", "IU/mL", "Negative"),
            ("Anti-HBe", "Hepatitis Panel", "IU/mL", "Negative"),
            ("Anti-HCV", "Hepatitis Panel", "IU/mL", "Negative"),
        ]
        #🧪 TORCH Panel
        items += [
            ("Toxoplasma IgG", "TORCH Panel", "IU/mL", "Negative"),
            ("Toxoplasma IgM", "TORCH Panel", "IU/mL", "Negative"),
            ("Rubella IgG", "TORCH Panel", "IU/mL", "Positive"),
            ("Rubella IgM", "TORCH Panel", "IU/mL", "Negative"),
            ("CMV IgG", "TORCH Panel", "IU/mL", "Positive"),
            ("CMV IgM", "TORCH Panel", "IU/mL", "Negative"),
            ("HSV-1 IgG", "TORCH Panel", "IU/mL", "Negative"),
            ("HSV-2 IgG", "TORCH Panel", "IU/mL", "Negative"),
        ]
        #🧠 ANA Profile
        items += [
            ("ANA (IFA)", "ANA Profile", "Ratio", "<1:40"),
            ("Anti-dsDNA", "ANA Profile", "IU/mL", "<30"),
            ("Anti-Sm", "ANA Profile", "IU/mL", "Negative"),
            ("Anti-RNP", "ANA Profile", "IU/mL", "Negative"),
            ("Anti-SSA (Ro)", "ANA Profile", "IU/mL", "Negative"),
            ("Anti-SSB (La)", "ANA Profile", "IU/mL", "Negative"),
            ("Anti-Scl-70", "ANA Profile", "IU/mL", "Negative"),
            ("Anti-Jo-1", "ANA Profile", "IU/mL", "Negative"),
        ]
        #🧪 Urinary Total Volume
        items += [
            ("Urinary Total Volume", "UTV (Urinary Total Volume)", "mL", "1000–2000"),
            ("Urine Protein", "UTV (Urinary Total Volume)", "mg/dL", "<150"),
            ("Urine Sugar", "UTV (Urinary Total Volume)", "Result", "Nil/Trace"),
        ]
        #🧪 UTP (24hr Urinary Total Protein)
        items += [
            ("Urinary Total Protein (24hr)", "UTP (24hr Urinary Total Protein)", "mg/day", "<150"),
            ("Urine Volume (24hr)", "UTP (24hr Urinary Total Protein)", "mL", "1000–2000"),
        ]
        #🧪 Urine For Pregnancy
        items += [
            ("Urine hCG", "Urine For Pregnency", "Result", "Negative"),
            ("Urine Sugar", "Urine For Pregnency", "Result", "Nil/Trace"),
            ("Urine Protein", "Urine For Pregnency", "Result", "Nil"),
        ]
        #🧪 Urine for Ketonbody
        items += [
            ("Urine Ketone", "Urine for ketonbody", "Result", "Negative"),
            ("Urine Sugar", "Urine for ketonbody", "Result", "Nil/Trace"),
        ]
        #🧪 Urine for ACR
        items += [
            ("Albumin", "Urine for ACR", "mg/L", "<30"),
            ("Creatinine", "Urine for ACR", "mg/dL", "Normal"),
            ("ACR Ratio", "Urine for ACR", "mg/g", "<30"),
        ]
        #🧪 Urine for PCR
        items += [
            ("Urine Protein", "Urine for PCR", "mg/dL", "<150"),
            ("Urine Creatinine", "Urine for PCR", "mg/dL", "Normal"),
            ("Protein/Creatinine Ratio", "Urine for PCR", "mg/g", "<150"),
        ]

        for name, group_name, unit, ref_range in items:
            TestItem.objects.get_or_create(name=name, group=group_map[group_name], defaults={
                "unit": unit,
                "reference_range": ref_range,
                "created_by": admin_user
        })

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
            ("Dr. Ahsan Habib", "internal", "Medicine", "Rangpur Medical", "01700000001"),
            ("Dr. Nusrat Jahan", "external", "Cardiology", "City Hospital", "01700000002"),
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