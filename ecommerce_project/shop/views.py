from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not username or not email or not password or not confirm:
            return render(request, 'signup.html', {'error': 'All fields are required'})

        if password != confirm:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'login.html', {'error': 'Please fill in all fields'})

        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            return render(request, 'login.html', {'error': 'User not found'})

        user = authenticate(request, username=user_obj.username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    cart_data = []
    total = 0
    for item in items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        cart_data.append({
            'id': item.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'subtotal': subtotal
        })
    return render(request, 'cart.html', {'cart_items': cart_data, 'total': total})

@login_required(login_url='/login/')
def increase_quantity(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('view_cart')

@login_required(login_url='/login/')
def decrease_quantity(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()  # Optional: remove item if quantity is 1
    return redirect('view_cart')
