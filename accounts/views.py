from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import Group
from django.contrib import messages
from .models import Customer, Product, Order
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only


# Create your views here.



####### REGISTER PAGE VIEW ########

# @unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            messages.success(request, f"Account was created successfully for {username}.")
            return redirect('login')
    context={'form':form}
    return render(request, 'accounts/register.html', context)

####### LOGIN PAGE VIEW ########

# @unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        ####### Implementation of login function and error handling #######
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, message="Username or Password is Incorrect.")
    context={}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

####### HOME PAGE VIEW ########

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_orders = orders.count()
    total_customers = customers.count()

    ####### Total number of status #######
    
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    ####### References #######

    context = {
        'orders': orders,
        'customers': customers,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'delivered': delivered,
        'pending': pending
    }
    return render(request, "accounts/dashboard.html", context)

####### USER #######


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {
        'orders':orders,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending
    }
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, "accounts/account_settings.html", context)

    ####### CUSTOMER PAGE VIEW #######

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    ####### References #######


    context = {
        'customer':customer,
        'orders':orders,
        'total_orders': total_orders,
        'myFilter': myFilter
    }
    return render(request, "accounts/customer.html", context)

    ####### PRODUCT PAGE VIEW #######

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, "accounts/products.html", {'products':products})

    ####### METHODS OF CRUD #######

    #CRUD OPERATION
    #1CREATE

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'), extra=5)
    customer = Customer.objects.get(id = pk)
    formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
    # form = OrderForm(initial={'customer':customer})
    if request.method=='POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    
    context = {'formset':formset}
    return render(request, 'accounts/order_form.html', context)

    #CRUD OPERATION
    #2UPDATE

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method=='POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid:
            form.save()
            return redirect('/')
    context = {'formset':form}
    return render(request, 'accounts/order_form.html', context)

    #CRUD OPERATION
    #3DELETE

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()

        return redirect('/')
    context = {
        'item': order,
        }
    return render(request, 'accounts/delete.html', context)