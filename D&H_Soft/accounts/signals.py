# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser, Profile, Role

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

    # apps.py এ দিতে হবে....
    #def ready(self):
    #    import accounts.signals  # ✅ Import signal here
