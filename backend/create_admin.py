import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@tenderlink.com')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(email=admin_email).exists():
    user = User.objects.create_superuser(
        username=admin_email,  # Using email as username per your specs
        email=admin_email,
        password=admin_password
    )
    user.role = 'super_admin'  # Ensure your custom role field is explicitly set
    user.save()
    print(f"Superadmin '{admin_email}' created successfully.")
else:
    print(f"Superadmin '{admin_email}' already exists. Skipping creation.")
