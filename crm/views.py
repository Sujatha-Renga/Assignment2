from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from django.shortcuts import redirect

from django.db.models import Sum
from _decimal import Decimal

from django.views.generic.base import View
import pdfkit
from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.template.loader import get_template

now = timezone.now()


def home(request):
    return render(request, 'crm/home.html',
                  {'crm': home})


# Create your views here.
@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'crm/customer_list.html',
                  {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'crm/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'crm/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('crm:customer_list')


@login_required
def service_list(request):
    service = Service.objects.filter(created_date__lte=timezone.now())
    return render(request, 'crm/service_list.html',
                  {'services': service})


@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        # update
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            service.updated_date = timezone.now()
            service.save()
            service = Service.objects.filter(created_date__lte=timezone.now())
            return render(request, 'crm/service_list.html',
                          {'services': service})
    else:
        # edit
        form = ServiceForm(instance=service)
    return render(request, 'crm/service_edit.html', {'form': form})


@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    return redirect('crm:service_list')


@login_required
def service_new(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.created_date = timezone.now()
            service.save()
            services = Service.objects.filter(created_date__lte=timezone.now())
            return render(request, 'crm/service_list.html',
                          {'services': services})
    else:
        form = ServiceForm()
        # print("Else")
    return render(request, 'crm/service_new.html', {'form': form})


@login_required
def product_list(request):
    product = Product.objects.filter(created_date__lte=timezone.now())
    return render(request, 'crm/product_list.html',
                  {'products': product})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        # update
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_date = timezone.now()
            product.save()
            product = Product.objects.filter(created_date__lte=timezone.now())
            return render(request, 'crm/product_list.html',
                          {'products': product})
    else:
        # edit
        form = ProductForm(instance=product)
    return render(request, 'crm/product_edit.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('crm:product_list')


@login_required
def product_new(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_date = timezone.now()
            product.save()
            product = Product.objects.filter(created_date__lte=timezone.now())
            return render(request, 'crm/product_list.html',
                          {'products': product})
    else:
        form = ProductForm()
        # print("Else")
    return render(request, 'crm/product_new.html', {'form': form})


@login_required
def summary(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    services = Service.objects.filter(cust_name=pk)
    products = Product.objects.filter(cust_name=pk)
    sum_service_charge = \
        Service.objects.filter(cust_name=pk).aggregate(Sum('service_charge'))
    sum_product_charge = \
        Product.objects.filter(cust_name=pk).aggregate(Sum('charge'))

    # if no product or service records exist for the customer,
    # change the ‘None’ returned by the query to 0.00
    sum = sum_product_charge.get("charge__sum")
    if sum == None:
        sum_product_charge = {'charge__sum': Decimal('0')}
    sum = sum_service_charge.get("service_charge__sum")
    if sum == None:
        sum_service_charge = {'service_charge__sum': Decimal('0')}

    return render(request, 'crm/summary.html', {'customer': customer,
                                                'products': products,
                                                'services': services,
                                                'sum_service_charge': sum_service_charge,
                                                'sum_product_charge': sum_product_charge, })


@login_required
def customer_pdf(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    services = Service.objects.filter(cust_name=pk)
    products = Product.objects.filter(cust_name=pk)
    sum_service_charge = Service.objects.filter(cust_name=pk).aggregate(Sum('service_charge'))
    sum_product_charge = Product.objects.filter(cust_name=pk).aggregate(Sum('charge'))
    template = get_template('crm/summary.html')
    html = template.render({'products': products,
                            'services': services,
                            'sum_service_charge': sum_service_charge,
                            'sum_product_charge': sum_product_charge,
                            'thecustomer': customer,
                            })
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(html, False, options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=customer' + str(pk) + '.pdf'
    return response
