from django.contrib.auth.base_user import BaseUserManager
import random

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email,username , password = None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email,username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db) 
        return user


    def create_superuser(self, email, username=None,password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email,username , password, **extra_fields)
     
