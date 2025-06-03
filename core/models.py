from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,phone,password=None,**extra_fields):
        if not phone:
            raise ValueError("The phone field must be set")
        else:
            user = self.model(phone=phone,**extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone, password, **extra_fields)
    
class User(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES = [
        ('COACH', 'Coach'),
        ('PLAYER', 'Player'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PLAYER')

    username = models.CharField(max_length=255)
    phone = models.CharField(unique=True,max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

# class phoneVerificationCode(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE)
#     code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def is_expired(self):
#         return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

