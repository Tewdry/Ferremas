from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views import View
from . models import Cart, Customer, Product
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.http import JsonResponse
from django.db.models import Q
import requests
from transbank.webpay.webpay_plus.transaction import Transaction

# Create your views here.

def home(request):
    return render(request,"app/home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
    
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Usuario Creado Correctamente!")
        else:
            messages.warning(request,"No se ha podido crear el Usuario")
        return render(request,"app/customerregistration.html",locals())
    
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,city=city,mobile=mobile,
                            state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Perfil guardado correctamente!')
        else:
            messages.warning(request,"No se ha podido guardar el perfil!")
        return render(request, 'app/profile.html',locals())
    
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Perfil actualizado correctamente!")
        else:
            messages.warning(request,"No se ha podido actualizar el perfil!")
        return redirect("address")

def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount * value
    totalamount = amount * 40
    return render(request, 'app/addtocart.html',locals())

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        return render(request, 'app/checkout.html',locals())
    
def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)


def convert_currency(request):
    if request.method == 'GET':
        amount = request.GET.get('amount')
        from_currency = request.GET.get('from_currency')
        to_currency = request.GET.get('to_currency')

        if not amount or not from_currency or not to_currency:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount'}, status=400)

        api_url = f'https://mindicador.cl/api/{from_currency}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if 'serie' in data:
                from_rate = data['serie'][0]['valor']
                to_rate = data['serie'][0]['valor']
                if from_currency != 'uf':
                    to_rate = requests.get(f'https://mindicador.cl/api/{to_currency}').json()['serie'][0]['valor']
                result = (amount / from_rate) * to_rate
                return JsonResponse({'result': result})
            else:
                return JsonResponse({'error': 'Invalid currency'}, status=400)
        else:
            return JsonResponse({'error': 'Failed to fetch exchange rates'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def api_view(request):
    api_url = 'https://mindicador.cl/api'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        
        # Lógica para convertir los datos de la API a otra moneda
        # Supongamos que queremos convertir el valor del dólar a pesos chilenos
        if 'dolar' in data:
            dolar_value = data['dolar']['valor']
            converted_value = dolar_value * 800 # Supongamos que 1 dólar equivale a 800 pesos chilenos
            data['dolar']['valor'] = converted_value
        
        return render(request, 'app/api_view.html', {'data': data})
    else:
        return JsonResponse({'error': 'Failed to fetch data from API'}, status=500)
    

def create_transaction(request):
    # Lógica para crear la transacción en Transbank
    # Aquí puedes utilizar el SDK de Transbank para crear la transacción

    # Después de crear la transacción, redirigir al usuario a la página de Transbank
    return redirect('https://www.transbank.cl/')  # Reemplaza con la URL de Transbank