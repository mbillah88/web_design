from django.core.management.base import BaseCommand
from django.urls import get_resolver
from accounts.models import Module  # Update with your actual app name

class Command(BaseCommand):
    help = 'Sync named URLs into Module table for sidebar/breadcrumb rendering'

    def handle(self, *args, **kwargs):
        resolver = get_resolver()
        url_names = [name for name in resolver.reverse_dict.keys() if isinstance(name, str)]
        added, skipped = 0, 0

        for url_name in url_names:
            if Module.objects.filter(url_name=url_name).exists():
                skipped += 1
                continue

            # Optional: Bangla name conversion logic
            name = url_name.replace('_', ' ').title()
            bangla_name = self.bangla_translate(name)

            Module.objects.create(
                name=bangla_name,
                url_name=url_name,
                parent=None,  # You can manually assign parent later
                icon='bi-circle',  # Default icon
                order=0
            )
            added += 1

        self.stdout.write(self.style.SUCCESS(f'{added} new modules added, {skipped} skipped'))

    def bangla_translate(self, name):
        # Optional: basic English-to-Bangla mapping
        mapping = {
            'Dashboard': 'ড্যাশবোর্ড',
            'Profile': 'প্রোফাইল',
            'Accounts': 'অ্যাকাউন্টস',
            'Products': 'পণ্য',
            'Settings': 'সেটিংস',
        }
        return mapping.get(name, name)
