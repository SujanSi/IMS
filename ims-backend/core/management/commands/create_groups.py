from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ims.models import CompanyInfo, Category, Unit, Product, Stock, Order, OrderItem  # Adjust according to your app name

class Command(BaseCommand):
    help = 'Create groups and assign permissions'

    def handle(self, *args, **kwargs):
        models = [CompanyInfo, Category, Unit, Product, Stock, Order, OrderItem]
        groups_permissions = {
            'Admin': ['add', 'change', 'delete', 'view'],
            'Manager': ['add', 'change', 'view'],
            'User': ['view'],
        }

        for group_name, actions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                for action in actions:
                    codename = f'{action}_{model._meta.model_name}'
                    permission, created = Permission.objects.get_or_create(
                        codename=codename,
                        content_type=content_type
                    )
                    group.permissions.add(permission)
            self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created/updated with permissions'))
