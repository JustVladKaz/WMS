import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from django.db.models import Sum, F
from .models import Report, Order, Product
from .forms import ProductForm, OrderForm
from django.http import HttpResponseForbidden
from django.utils.timezone import now, timedelta, localdate
from .tasks import generate_daily_sales_report

def user_login(request):  # login view
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)  # authenticate the user
        if user is not None:  # check if authentication was successful
            if user.is_active:
                login(request, user)  # log the user in
                return redirect("redirect_after_login")  # redirect based on user role
            else:
                messages.warning(request, "your account is inactive.")  # show error if account is inactive
        else:
            messages.warning(request, "invalid username or password.")  # show error for invalid credentials
    return render(request, "login.html")

def user_logout(request):  # Logout View
    logout(request)
    return redirect("/login/")

@login_required  # create product (only admins)
@role_required(allowed_roles=["admin"])
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():  # check if the form data is valid
            form.save()  # save the new product
            messages.success(request, "product added successfully!")
            return redirect("product_list")  # redirect to the product list after adding
        else:
            messages.warning(request, "error adding product ! make sure all the fields are filled properly.")  # display an error message if form is invalid
    else:
        form = ProductForm()  # initialize an empty product form for get requests
    return render(request, "products/product_form.html", {"form": form})  # render the product creation form

@login_required  # view all products (accessible to everyone)
def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})

@login_required  # update product (only admins)
@role_required(allowed_roles=["admin"])
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # get the product or return a 404 error if not found
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product) 
        if form.is_valid():  # check if the form data is valid
            form.save()  # save the updated product details
            return redirect("product_list")  # redirect to the product list after updating
    else:
        form = ProductForm(instance=product)  # initialize the form with the existing product details
    return render(request, "products/product_form.html", {"form": form})

@login_required  # delete product (only admins)
@role_required(allowed_roles=["admin"])
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete() # delete product
        return redirect("product_list")
    return render(request, "products/product_confirm_delete.html", {"product": product})

@login_required  # create orders (employee only)
@role_required(allowed_roles=["employee"])
def order_create(request):
    products = Product.objects.filter(quantity__gt=0)  # get all products that are in stock
    form = OrderForm()  # initialize an empty order form
    if request.method == "POST":
        form = OrderForm(request.POST)  # populate the form with submitted data
        if form.is_valid():
            order = form.save(commit=False)  # create an order instance but do not save it yet
            order.ordered_by = request.user  # assign the current user as the one placing the order
            if order.quantity <= 0:  # prevent ordering zero or negative quantities
                messages.error(request, "invalid quantity!")
                return redirect("order_create")
            if not Product.objects.filter(id=order.product.id).exists():  # ensure the selected product exists
                messages.error(request, "invalid product selection!")
                return redirect("order_create")
            try:
                order.save()  # save the order if everything is valid
                messages.success(request, "order placed successfully!")
                return redirect("employee_orders")  # redirect to the employee's order list
            except ValueError:  # catch errors if stock is insufficient
                messages.warning(request, "not enough stock available!")
    return render(request, "orders/order_form.html", {"form": form, "products": products})

@login_required  # view employee’s own orders
@role_required(allowed_roles=["employee"])
def employee_orders(request):
    orders = Order.objects.filter(ordered_by=request.user).order_by("-ordered_at")
    return render(request, "orders/employee_orders.html", {"orders": orders})

@login_required # cancel order (for employees)
@role_required(allowed_roles=["employee"])
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, ordered_by=request.user)
    if order.status == "pending": # order can only be canceled if it is still pending
        order.status = "canceled"
        order.save() # order save will take care of adding the quantity canceled to the stock
        messages.success(request, "Order canceled successfully.")
    else: # order can only be canceled if it is still pending
        messages.error(request, "This order cannot be canceled.") 
    return redirect("employee_orders")

@login_required  # view all orders (Admins Only)
@role_required(allowed_roles=["admin"])
def order_list(request):
    orders = Order.objects.select_related("product").order_by("-ordered_at")
    return render(request, "orders/order_list.html", {"orders": orders})

@login_required  # update employee's orders status
@role_required(allowed_roles=["admin"])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id) # if the order does not exist return a 404 error
    if request.method == "POST":
        new_status = request.POST.get("status", "").strip().lower() # retrieve new status, remove extra spaces, and convert to lowercase
        valid_statuses = {status[0] for status in Order.STATUS_CHOICES}
        if new_status not in valid_statuses: # check if the provided status is valid
            messages.error(request, "Invalid status update!")
            return redirect("order_list")
        if order.status == new_status: #if the status is already set to the same value notify the admin
            messages.info(request, "Order status is already set.")
            return redirect("order_list")
        order.status = new_status # update order status
        order.save()
        messages.success(request, f"Order status updated to {new_status.capitalize()}!") # display a success message
    return redirect("order_list")

@login_required  # view reports (admin only)
@role_required(allowed_roles=["admin"])
def report_list(request):
    reports = Report.objects.all().order_by("-generated_at") # get reports ordered from last to first
    return render(request, "reports/report_list.html", {"reports": reports})

@login_required  # generate sales report (admin only)
@role_required(allowed_roles=["admin"])
def generate_sales_report(request):
    today = now().date()  # today's date
    # delete any existing report for today to avoid duplicates
    Report.objects.filter(report_type="sales", generated_at__date=today).delete()
    generate_daily_sales_report()
    messages.success(request, "Daily sales report generated successfully!")
    return redirect("report_list")

@login_required  # generate low stock alerts (admin only)
@role_required(allowed_roles=["admin"])
def generate_low_stock_alert(request):
    low_stock_products = Product.objects.filter(quantity__lte=5) # check product's quantity below 5
    if low_stock_products.exists(): # if true (there is a product's quantity under 5)
        report_details = "\n".join([f"{product.name}: Only {product.quantity} left!" for product in low_stock_products])
        Report.objects.create(report_type="low_stock", details=report_details)
        messages.warning(request, "Low-stock alert generated!")
    else:  # else (there is not a single product's quantity under 5)
        messages.info(request, "All products are sufficiently stocked.")
    return redirect("report_list")

@login_required  # dashboard (admin only)
@role_required(allowed_roles=["admin"])
def admin_dashboard(request):
    first_day_of_month = now().replace(day=1)  # first day of the current month
    # get filter from request (default: completed orders only)
    order_filter = request.GET.get("order_filter", "completed")
    # base query (completed orders only)
    orders_query = Order.objects.filter(status="completed", ordered_at__gte=first_day_of_month)
    # if admin selects "all", include admin-canceled orders
    if order_filter == "all":
        orders_query = Order.objects.filter(status__in=["completed", "canceled"], ordered_at__gte=first_day_of_month)
    # get top 5 most ordered products based on the selected filter
    top_products = (
        orders_query.values("product__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )
    product_names = [item["product__name"] for item in top_products]
    total_quantities = [item["total_quantity"] for item in top_products]
    period = request.GET.get("period", "day")
    if period == "day":  # last 7 days orders
        time_range = [now().date() - timedelta(days=i) for i in range(6, -1, -1)]
        time_labels = [date.strftime("%b %d") for date in time_range]
        time_orders = [
            Order.objects.filter(ordered_at__date=date, status="completed").count()
            for date in time_range]
    elif period == "week":  # Last 4 weeks
        end_of_week = localdate()  # Get today's date
        start_of_week = end_of_week - timedelta(weeks=3)  # Start from 4 weeks ago
        time_range = [start_of_week + timedelta(weeks=i) for i in range(4)]
        time_labels = [f"Week {i+1}" for i in range(4)]
        time_orders = [
            Order.objects.filter(
                ordered_at__gte=time_range[i],
                ordered_at__lt=time_range[i+1] if i+1 < len(time_range) else end_of_week + timedelta(days=1),
                status="completed"  
            ).count()
            for i in range(4)
        ]
    elif period == "month":  # last 12 months orders
        time_range = [now().replace(day=1) - timedelta(days=30*i) for i in range(11, -1, -1)]
        time_labels = [date.strftime("%b %Y") for date in time_range]
        time_orders = [
            Order.objects.filter(ordered_at__year=date.year, ordered_at__month=date.month, status="completed").count()
            for date in time_range]
    total_reports = Report.objects.count()
    total_revenue = (
        Order.objects.filter(status="completed", ordered_at__date=localdate())
        .aggregate(total_revenue=Sum(F("product__price") * F("quantity")))
        ["total_revenue"] or 0
    )
    pending_orders = Order.objects.filter(status="pending").count()  
    canceled_orders = Order.objects.filter(status="canceled", ordered_at__gte=now() - timedelta(days=30)).count()  
    total_orders_last_30_days = Order.objects.filter(ordered_at__gte=now() - timedelta(days=30)).count()   
    canceled_order_rate = (canceled_orders / total_orders_last_30_days * 100) if total_orders_last_30_days else 0  
    low_stock_products = Product.objects.filter(quantity__lte=5).count()  
    context = {
        "total_products": Product.objects.count(),
        "total_orders": Order.objects.count(),
        "total_reports": total_reports,
        "product_names": json.dumps(product_names),
        "total_quantities": json.dumps(total_quantities),
        "time_labels": json.dumps(time_labels),
        "time_orders": json.dumps(time_orders),
        "current_period": period,
        "current_filter": order_filter,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "canceled_order_rate": canceled_order_rate,
        "low_stock_products": low_stock_products,}
    return render(request, "admin_dashboard.html", context)

def custom_login_redirect(request): # login redirection 
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("admin_dashboard") # this will redirect the admin to the dashboard
        elif request.user.role == "employee":
            return redirect("employee_orders") # this will redirect the employee to the orders list
    return redirect("login") # if the user isn't authenticated he will be directed to the login page

def check_permission(user, role_required): # check permissions for all users
    if user.role != role_required: # to prevent accessing pages without the permission 
        return HttpResponseForbidden("You do not have permission to access this page.")
    return None
