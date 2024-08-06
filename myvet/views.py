from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import Product, Client, Vaccine, Pet, PetType, ProductType, VaccineType
from .serializers import ProductSerializer, PetSerializer, ClientSerializer, VaccineSerializer, PetTypeSerializer, ProductTypeSerializer, VaccineTypeSerializer
from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .auth_backends import EmailBackend

@api_view(['POST'])
def custom_login(request):
    email = request.POST["email"]
    password = request.POST["password"]
    pub_date = request.POST["pub_date"]

    user = EmailBackend.authenticate(request, email=email, password=password)
    serializer = ClientSerializer(user)

    if user is False:
        return Response({ 'message': 'Wrong Password' }, status=401)
    
    if user is None:
        user = Client(email=email, password=password, pub_date=pub_date)
        user.set_password(user.password)
        user.save()
        serializer = ClientSerializer(user)

    login(request, user, backend='myvet.auth_backends.EmailBackend')
    return Response(serializer.data, status=200)

@api_view(['POST'])
def custom_logout(request):
    logout(request)
    return Response({'message': 'Logout successfully'}, status=200)

@api_view(['POST'])
def reset_password(request):
    email = request.POST["email"]
    password = request.POST["password"]

    user = EmailBackend.authenticate(request, email=email, password=password)

    if user is not None:
        user.set_password(user.password)
        user.save()
    return Response({'message': 'Reset Password successfully'}, status=200)
        
class Pets_ApiView(APIView):
    def get(self, request):
        pet_type = request.query_params.get('petType', None)
        value = request.query_params.get('value', '')
        if pet_type is not None:
            data = Pet.objects.filter(type=pet_type)
        else:
            data = Pet.objects.filter(Q(name__icontains=value))
                
        serializer = PetSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PetSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class Pet_ApiView(APIView):
    def get(self, request, id):
        pet = get_list_or_404(Pet, id=id)
        serializer = PetSerializer(pet, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        pet = get_object_or_404(Pet, id=id)
        new_owner_id = request.data.get('owner')
        new_owner = get_object_or_404(Client, id=new_owner_id) if new_owner_id else None
        current_owner = pet.owner

        if current_owner:
            current_owner_pets = current_owner.pets or []
            current_owner_pets = [p for p in current_owner_pets if p['id'] != pet.id]
            current_owner.pets = current_owner_pets
            current_owner.save()

        if new_owner:
            new_owner_pets = new_owner.pets or []
            if not any(p['id'] == pet.id for p in new_owner_pets):
                new_owner_pets.append({"id": pet.id, "name": pet.name})
            new_owner.pets = new_owner_pets
            new_owner.save()

        serializer = PetSerializer(pet, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        pet = get_object_or_404(Pet, id=id)
        serializer = PetSerializer(pet)
        owner = pet.owner
        
        if owner:
            pets = owner.pets or []
            updated_pets = [p for p in pets if p['id'] != pet.id]
            owner.pets = updated_pets
            owner.save()

        pet.delete()
        return Response(serializer.data, status=200)
    
class Products_ApiView(APIView):
    def get(self, request):
        product_type = request.query_params.get('productType', None)
        product_pet_type = request.query_params.get('productPetType', None)
        value = request.query_params.get('value', '')

        if product_type is not None and product_pet_type is not None:
            data = Product.objects.filter(Q(type=product_type) | Q(pet_type=product_pet_type) | Q(name__icontains=value) | Q(description__icontains=value))
        else:
            data = Product.objects.filter(Q(name__icontains=value) | Q(description__icontains=value))
                
        serializer = ProductSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
class Product_ApiView(APIView):
    def get(self, request, id):
        product = get_list_or_404(Product, id=id)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=200)
    
class Clients_ApiView(APIView):
    def get(self, request):
        value = request.query_params.get('value', '')
        data = Client.objects.filter(Q(name__icontains=value) | Q(surname__icontains=value) | Q(dni__icontains=value))
                
        serializer = ClientSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class Client_ApiView(APIView):
    def get(self, request, id):
        user = get_list_or_404(Client, id=id)
        serializer = ClientSerializer(user, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        email = request.data.get('email')
        name = request.data.get('name')
        surname = request.data.get('surname')

        admin_user = None

        user = get_object_or_404(Client, id=id)
        serializer = ClientSerializer(user, data=request.data)

        try:
            admin_user = User.objects.get(username=email)
            admin_user.first_name = name
            admin_user.last_name = surname
            admin_user.email = email
            admin_user.username = email
            admin_user.save()

        except User.DoesNotExist:
            pass

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)   
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        user = get_object_or_404(Client, id=id)

        try:
            admin_user = User.objects.get(email=request.get['email'])
            admin_user.delete()
        except admin_user is None:
            pass

        user.delete()
        serializer = ClientSerializer(user)
        return Response(serializer.data, status=200)
    
class Vaccines_ApiView(APIView):
    def get(self, request):
        vaccine_type = request.query_params.get('vaccineType', None)
        if vaccine_type is not None:
            data = Vaccine.objects.filter(type=vaccine_type)
        else:
            data = Vaccine.objects.all()
        serializer = VaccineSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VaccineSerializer(data=request.data)

        if serializer.is_valid():
            vaccine = serializer.save()
            pet = vaccine.pet
            
            pet_vaccines = pet.vaccines or []
            pet_vaccines.append({
                'id': vaccine.id,
                'name': vaccine.type.name,
                'app_date': vaccine.app_date.isoformat(),
            })
            pet.vaccines = pet_vaccines
            pet.save()
            
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class Vaccine_ApiView(APIView):
    def get(self, request, id):
        vaccine = get_list_or_404(Vaccine, id=id)
        serializer = VaccineSerializer(vaccine, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        vaccine = get_object_or_404(Vaccine, id=id)
        serializer = VaccineSerializer(vaccine, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        vaccine = get_object_or_404(Vaccine, id=id)
        vaccine.delete()
        serializer = VaccineSerializer(vaccine)
        return Response(serializer.data, status=200)
    
class PetTypes_ApiView(APIView):
    def get(self, request):
        pet_type = request.query_params.get('petType', None)
        value = request.query_params.get('value', '')
        if pet_type is not None:
            data = PetType.objects.filter(type=pet_type)
        else:
            data = PetType.objects.filter(Q(name__icontains=value))
                
        serializer = PetTypeSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PetTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class PetType_ApiView(APIView):
    def get(self, request, id):
        pet_type = get_list_or_404(PetType, id=id)
        serializer = PetTypeSerializer(pet_type, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        pet_type = get_object_or_404(PetType, id=id)
        serializer = PetTypeSerializer(pet_type, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        pet_type = get_object_or_404(PetType, id=id)
        pet_type.delete()
        serializer = PetTypeSerializer(pet_type)
        return Response(serializer.data, status=200)
    
class ProductTypes_ApiView(APIView):
    def get(self, request):
        product_type = request.query_params.get('productType', None)
        value = request.query_params.get('value', '')
        if product_type is not None:
            data = ProductType.objects.filter(type=product_type)
        else:
            data = ProductType.objects.filter(Q(name__icontains=value))
                
        serializer = ProductTypeSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class ProductType_ApiView(APIView):
    def get(self, request, id):
        product_type = get_list_or_404(ProductType, id=id)
        serializer = ProductTypeSerializer(product_type, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        product_type = get_object_or_404(ProductType, id=id)
        serializer = ProductTypeSerializer(product_type, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        product_type = get_object_or_404(ProductType, id=id)
        product_type.delete()
        serializer = ProductTypeSerializer(product_type)
        return Response(serializer.data, status=200)

class VaccineTypes_ApiView(APIView):
    def get(self, request):
        vaccine_type = request.query_params.get('vaccineType', None)
        value = request.query_params.get('value', '')
        if vaccine_type is not None:
            data = VaccineType.objects.filter(type=vaccine_type)
        else:
            data = VaccineType.objects.filter(Q(name__icontains=value))
                
        serializer = VaccineTypeSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VaccineTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
    
class VaccineType_ApiView(APIView):
    def get(self, request, id):
        vaccine_type = get_list_or_404(VaccineType, id=id)
        serializer = VaccineTypeSerializer(vaccine_type, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        vaccine_type = get_object_or_404(VaccineType, id=id)
        serializer = VaccineTypeSerializer(vaccine_type, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
            
        return Response(serializer.errors, status=400)
        
    def delete(self, request, id):
        vaccine_type = get_object_or_404(VaccineType, id=id)
        vaccine_type.delete()
        serializer = VaccineTypeSerializer(vaccine_type)
        return Response(serializer.data, status=200)