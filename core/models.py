from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from uuid import uuid4
from django.utils import timezone
from .hashers import MyCustomPasswordHasher




    
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    ADMIN = 'admin'
    RETAILER = 'retailer'
    API_USER = 'api_user'
    USER = 'user'
    
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (RETAILER, 'Retailer'),
        (API_USER, 'Api user'),
        (USER, 'User'),
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='user')
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=210, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True)
    image = models.ImageField(upload_to='profile/images', null=True, blank=True)
    bonuce = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)  

    referral_code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    referral_or_promo_code = models.CharField(max_length=8, null=True, blank=True)
    # Define other fields



    objects = UserManager()

    
 
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'gender', 'phone', 'address', 'birth_date', 'image', 'referral_or_promo_code']  # Add 'username' to REQUIRED_FIELDS


    class Meta:
        # Make sure to specify 'AbstractUser' as the base model
        abstract = False




    def __str__(self):
        return self.username
    

    def set_password(self, raw_password):
        """
        Hash the password using the custom password hasher.
        """
        hasher = MyCustomPasswordHasher()  # Instantiate your custom password hasher
        self.password = hasher.encode(raw_password, hasher.salt())  # Hash the password

    def check_password(self, raw_password):
        """
        Verify the raw password using the custom password hasher's verify method.
        """
        hasher = MyCustomPasswordHasher()  # Instantiate your custom password hasher
        return hasher.verify(raw_password, self.password)



    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_referral_code()
            referral_or_promo_code = self.referral_or_promo_code


            # Check if referral_or_promo_code is provided
            if referral_or_promo_code:
                # Handle referral bonuce
                try:
                    referred_by = get_user_model().objects.get(referral_code=referral_or_promo_code)
                    bonuce = Bonuce.objects.get(bonuce_type='referral').amount
                    self.bonuce += bonuce
                    referred_by.bonuce += bonuce
                    referred_by.save()
                except ObjectDoesNotExist:
                    pass  # Handle if referred_by does not exist

                # Handle promo bonuce
                try:
                    promo = PromoCode.objects.get(promo_code=referral_or_promo_code)
                    difference = timezone.now() - promo.created_at
                    if difference.days <= promo.validity_days:
                        self.bonuce += promo.amount
                except ObjectDoesNotExist:
                    pass  # Handle if promo does not exist


        super().save(*args, **kwargs)

def generate_referral_code():
    # Generate a unique referral code, you can customize this as needed
    # For example, generate a random alphanumeric code
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))



class PromoCode(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    promo_code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    amount = models.FloatField(default=0.0)
    validity_days = models.IntegerField(default=7)  # Validity in days
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.promo_code:
            # Generate promo code only if it's not set
            self.promo_code = generate_referral_code()
        super().save(*args, **kwargs)


class Bonuce(models.Model):
    REFERRAL = 'referral'
    NEW_YEAR = 'new_year'
    BONUCE_TYPE_CHOICES = [
        (REFERRAL, 'Referral bonuce'),
        (NEW_YEAR, 'New year bonuce'),
        # Add more choices as needed
    ]
    bonuce_type = models.CharField(max_length=20, choices=BONUCE_TYPE_CHOICES)
    amount = models.FloatField(default=0.0)  





    