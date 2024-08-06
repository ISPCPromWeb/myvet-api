import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

class NoHashFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # Check if the file name already exists, delete if it does
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name
class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class ProductType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class PetType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
class VaccineType(models.Model):
    name = models.CharField(max_length=200)
    pet_type = models.ForeignKey('PetType', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.IntegerField(default=100)
    type = models.ForeignKey('ProductType', on_delete=models.CASCADE)
    pet_type = models.ForeignKey('PetType', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='images/', storage=NoHashFileSystemStorage(), max_length=10000, null=True)
    pub_date = models.DateTimeField("Date Published", default=timezone.now)

    def __str__(self):
        return self.name

class Pet(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(PetType, on_delete=models.CASCADE)
    breed = models.CharField(max_length=200, default="")
    age = models.IntegerField(default=100)
    owner = models.ForeignKey('Client', null=True, on_delete=models.CASCADE)
    vaccines = models.JSONField(blank=True, null=True, default=[])
    pub_date = models.DateTimeField("Date Published", default=timezone.now)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.owner:
            owner = self.owner
            pets = owner.pets or []
            pet_ids = [pet['id'] for pet in pets if 'id' in pet]
            
            if self.id not in pet_ids:
                pets.append({
                    'id': self.id,
                    'name': self.name,
                    'type': self.type_id,
                    'breed': self.breed,
                    'age': self.age,
                    'vaccines': self.vaccines,
                    'pub_date': self.pub_date.isoformat()
                })
                owner.pets = pets
                owner.save()  # Save the updated client instance

class Client(AbstractBaseUser):
    name = models.CharField(max_length=200, default="")
    surname = models.CharField(max_length=200, default="")
    dni = models.IntegerField(default=0)
    address = models.CharField(max_length=200, default="")
    email = models.EmailField()
    phone = models.CharField(default="")
    password = models.CharField()
    pets = models.JSONField(blank=True, null=True, default=[])
    level = models.IntegerField(default=0)
    last_login = models.DateTimeField("Last Login", null=True, default=None)
    pub_date = models.DateTimeField("Date Published", default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = ClientManager()

    def __str__(self):
        return self.name
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        is_correct = super().check_password(raw_password)
        return is_correct
    
class Vaccine(models.Model):
    type = models.ForeignKey('VaccineType', on_delete=models.CASCADE)
    app_date = models.DateTimeField("Application Date")
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE)

    def __str__(self):
        return self.type.name

@receiver(post_save, sender=User)
def create_or_update_client(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(
            name=instance.first_name,
            surname=instance.last_name,
            email=instance.username,
            password=instance.password,
            level=1,
            pub_date=timezone.now()
        )
    else:
        try:
            client = Client.objects.get(email=instance.email)
            client.name = instance.first_name
            client.surname = instance.last_name
            client.email = instance.email
            client.password = instance.password
            client.save()
        except Client.DoesNotExist:
            pass