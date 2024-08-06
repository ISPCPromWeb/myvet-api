from rest_framework import serializers
from .models import Product, Pet, Client, Vaccine, PetType, VaccineType, ProductType
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        client = Client(**validated_data)
        if password is not None:
            client.set_password(password)
        client.save()
        return client

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = '__all__'

class PetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetType
        fields = '__all__'

class VaccineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineType
        fields = '__all__'

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'