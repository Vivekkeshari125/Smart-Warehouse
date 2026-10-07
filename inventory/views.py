from collections import deque

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib import messages

from .models import Product, Order, StockTransaction, Alert


# ============================================================
# HOME
# ============================================================

def home(request):
    return redirect('dashboard')


# ============================================================
# DSA - BUBBLE SORT
# ============================================================

def sort_products(products, sort_by='name'):

    products = list(products)

    n = len(products)

    for i in range(n):

        for j in range(0, n - i - 1):

            if sort_by == 'name':

                value1 = products[j].product_name.lower()
                value2 = products[j + 1].product_name.lower()

            elif sort_by == 'quantity':

                value1 = products[j].quantity
                value2 = products[j + 1].quantity

            elif sort_by == 'price':

                value1 = getattr(products[j], 'price', 0)
                value2 = getattr(products[j + 1], 'price', 0)

            elif sort_by == 'stock':

                value1 = products[j].minimum_stock
                value2 = products[j + 1].minimum_stock

            else:

                value1 = products[j].id
                value2 = products[j + 1].id

            if value1 > value2:

                products[j], products[j + 1] = (
                    products[j + 1],
                    products[j]
                )

    return products


# ============================================================
# DSA - HASHING SEARCH
# ============================================================

def search_product_by_id(product_id):

    all_products = Product.objects.all()

    product_hash_table = {
        product.id: product
        for product in all_products
    }

    return product_hash_table.get(product_id)


# ============================================================
# DSA - LINEAR SEARCH
# ============================================================

def linear_search_product(products, product_id):

    for product in products:

        if product.id == product_id:

            return product

    return None


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(request):

    products = Product.objects.all()

    total_products = products.count()

    total_stock = products.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    low_stock = products.filter(
        quantity__gt=0,
        quantity__lt=__import__('django').db.models.F('minimum_stock')
    ).count()

    out_of_stock = products.filter(
        quantity=0
    ).count()

    pending_orders = Order.objects.filter(
        status='Pending'
    ).count()

    completed_orders = Order.objects.filter(
        status='Completed'
    ).count()

    recent_transactions = StockTransaction.objects.select_related(
        'product'
    ).order_by('-timestamp')[:10]

    recent_orders = Order.objects.select_related(
        'product'
    ).order_by('-date')[:10]

    alerts = Alert.objects.select_related(
        'product'
    ).filter(
        status='Unread'
    ).order_by('-timestamp')[:10]

    context = {

        'total_products': total_products,

        'total_stock': total_stock,

        'low_stock': low_stock,

        'out_of_stock': out_of_stock,

        'pending_orders': pending_orders,

        'completed_orders': completed_orders,

        'recent_transactions': recent_transactions,

        'recent_orders': recent_orders,

        'alerts': alerts,

    }

    return render(
        request,
        'dashboard.html',
        context
    )


# ============================================================
# PRODUCTS
# ============================================================

def products(request):

    products_list = Product.objects.all()

    search = request.GET.get(
        'search',
        ''
    ).strip()

    category = request.GET.get(
        'category',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    ).strip()

    sort_by = request.GET.get(
        'sort',
        'name'
    )

    if search:

        products_list = products_list.filter(
            product_name__icontains=search
        )

    if category:

        products_list = products_list.filter(
            category=category
        )

    if status == 'low':

        products_list = products_list.filter(
            quantity__gt=0
        ).filter(
            quantity__lt=__import__('django').db.models.F('minimum_stock')
        )

    elif status == 'out':

        products_list = products_list.filter(
            quantity=0
        )

    elif status == 'in':

        products_list = products_list.filter(
            quantity__gte=__import__('django').db.models.F('minimum_stock')
        )

    products_list = sort_products(
        products_list,
        sort_by
    )

    categories = Product.objects.values_list(
        'category',
        flat=True
    ).distinct()

    context = {

        'products': products_list,

        'categories': categories,

        'search': search,

        'selected_category': category,

        'selected_status': status,

        'selected_sort': sort_by,

    }

    return render(
        request,
        'products.html',
        context
    )


# ============================================================
# ADD PRODUCT
# ============================================================

def add_product(request):

    if request.method == 'POST':

        product_name = request.POST.get(
            'product_name',
            ''
        ).strip()

        category = request.POST.get(
            'category',
            ''
        ).strip()

        quantity = request.POST.get(
            'quantity',
            '0'
        )

        minimum_stock = request.POST.get(
            'minimum_stock',
            '0'
        )

        if product_name and category:

            Product.objects.create(

                product_name=product_name,

                category=category,

                quantity=int(quantity),

                minimum_stock=int(minimum_stock)

            )

            messages.success(
                request,
                'Product added successfully.'
            )

            return redirect('products')

    return render(
        request,
        'add_product.html'
    )


# ============================================================
# PRODUCT SEARCH
# ============================================================

def product_search(request):

    product = None

    search_id = ''

    search_method = ''

    if request.method == 'POST':

        search_id = request.POST.get(
            'product_id',
            ''
        ).strip()

        search_method = request.POST.get(
            'search_method',
            'hashing'
        )

        if search_id.isdigit():

            product_id = int(search_id)

            if search_method == 'linear':

                all_products = Product.objects.all()

                product = linear_search_product(
                    all_products,
                    product_id
                )

            else:

                product = search_product_by_id(
                    product_id
                )

    context = {

        'product': product,

        'search_id': search_id,

        'search_method': search_method,

    }

    return render(
        request,
        'product_search.html',
        context
    )


# ============================================================
# INVENTORY
# ============================================================

def inventory(request):

    products_list = Product.objects.all().order_by(
        'product_name'
    )

    return render(
        request,
        'inventory.html',
        {
            'products': products_list
        }
    )


# ============================================================
# UPDATE STOCK
# ============================================================

def update_stock(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        new_quantity = request.POST.get(
            'quantity',
            '0'
        )

        try:

            new_quantity = int(new_quantity)

            if new_quantity < 0:

                messages.error(
                    request,
                    'Stock cannot be negative.'
                )

                return redirect('inventory')

            previous_quantity = product.quantity

            product.quantity = new_quantity

            product.save()

            StockTransaction.objects.create(

                product=product,

                transaction_type='Stock In'
                if new_quantity > previous_quantity
                else 'Stock Out',

                quantity=abs(
                    new_quantity - previous_quantity
                ),

                previous_quantity=previous_quantity,

                updated_quantity=new_quantity

            )

            messages.success(
                request,
                'Stock updated successfully.'
            )

        except ValueError:

            messages.error(
                request,
                'Please enter a valid quantity.'
            )

    return redirect('inventory')


# ============================================================
# STOCK IN
# ============================================================

def stock_in(request):

    products = Product.objects.all()

    if request.method == 'POST':

        product_id = request.POST.get(
            'product'
        )

        quantity = request.POST.get(
            'quantity',
            '0'
        )

        reference = request.POST.get(
            'reference',
            ''
        )

        notes = request.POST.get(
            'notes',
            ''
        )

        product = get_object_or_404(
            Product,
            id=product_id
        )

        try:

            quantity = int(quantity)

            if quantity <= 0:

                messages.error(
                    request,
                    'Quantity must be greater than zero.'
                )

                return redirect('stock_in')

            previous_quantity = product.quantity

            product.quantity += quantity

            product.save()

            StockTransaction.objects.create(

                product=product,

                transaction_type='Stock In',

                quantity=quantity,

                previous_quantity=previous_quantity,

                updated_quantity=product.quantity,

                reference=reference,

                notes=notes

            )

            messages.success(
                request,
                'Stock added successfully.'
            )

            return redirect('inventory')

        except ValueError:

            messages.error(
                request,
                'Please enter a valid quantity.'
            )

    return render(
        request,
        'stock_in.html',
        {
            'products': products
        }
    )


# ============================================================
# STOCK OUT
# ============================================================

def stock_out(request):

    products = Product.objects.all()

    if request.method == 'POST':

        product_id = request.POST.get(
            'product'
        )

        quantity = request.POST.get(
            'quantity',
            '0'
        )

        reference = request.POST.get(
            'reference',
            ''
        )

        notes = request.POST.get(
            'notes',
            ''
        )

        product = get_object_or_404(
            Product,
            id=product_id
        )

        try:

            quantity = int(quantity)

            if quantity <= 0:

                messages.error(
                    request,
                    'Quantity must be greater than zero.'
                )

                return redirect('stock_out')

            if quantity > product.quantity:

                messages.error(
                    request,
                    'Insufficient stock.'
                )

                return redirect('stock_out')

            previous_quantity = product.quantity

            product.quantity -= quantity

            product.save()

            StockTransaction.objects.create(

                product=product,

                transaction_type='Stock Out',

                quantity=quantity,

                previous_quantity=previous_quantity,

                updated_quantity=product.quantity,

                reference=reference,

                notes=notes

            )

            messages.success(
                request,
                'Stock removed successfully.'
            )

            return redirect('inventory')

        except ValueError:

            messages.error(
                request,
                'Please enter a valid quantity.'
            )

    return render(
        request,
        'stock_out.html',
        {
            'products': products
        }
    )


# ============================================================
# ORDERS
# ============================================================

def orders(request):

    order_list = Order.objects.select_related(
        'product'
    ).order_by(
        '-date'
    )

    return render(
        request,
        'orders.html',
        {
            'orders': order_list
        }
    )


# ============================================================
# ADD ORDER
# ============================================================

def add_order(request):

    products = Product.objects.all()

    if request.method == 'POST':

        customer = request.POST.get(
            'customer',
            ''
        ).strip()

        product_id = request.POST.get(
            'product'
        )

        quantity = request.POST.get(
            'quantity',
            '1'
        )

        product = get_object_or_404(
            Product,
            id=product_id
        )

        try:

            quantity = int(quantity)

            if quantity <= 0:

                messages.error(
                    request,
                    'Quantity must be greater than zero.'
                )

                return redirect('add_order')

            if quantity > product.quantity:

                messages.error(
                    request,
                    'Insufficient stock.'
                )

                return redirect('add_order')

            total = quantity * 500

            Order.objects.create(

                customer=customer,

                product=product,

                quantity=quantity,

                status='Pending',

                total=total

            )

            messages.success(
                request,
                'Order created successfully.'
            )

            return redirect('orders')

        except ValueError:

            messages.error(
                request,
                'Please enter a valid quantity.'
            )

    return render(
        request,
        'add_order.html',
        {
            'products': products
        }
    )


# ============================================================
# COMPLETE ORDER
# ============================================================

def complete_order(request, order_id):

    order = get_object_or_404(
        Order,
        order_id=order_id
    )

    if order.status == 'Completed':

        messages.info(
            request,
            'Order is already completed.'
        )

        return redirect('orders')

    if order.product is None:

        messages.error(
            request,
            'This order has no product.'
        )

        return redirect('orders')

    product = order.product

    if order.quantity > product.quantity:

        messages.error(
            request,
            'Insufficient stock to complete this order.'
        )

        return redirect('orders')

    previous_quantity = product.quantity

    product.quantity -= order.quantity

    product.save()

    order.status = 'Completed'

    order.save()

    StockTransaction.objects.create(

        product=product,

        transaction_type='Stock Out',

        quantity=order.quantity,

        previous_quantity=previous_quantity,

        updated_quantity=product.quantity,

        reference=f'Order #{order.order_id}',

        notes='Stock reduced after order completion.'

    )

    messages.success(
        request,
        'Order completed and stock updated.'
    )

    return redirect('orders')


# ============================================================
# DSA - QUEUE
# ============================================================

def process_next_order(request):

    pending_orders = Order.objects.filter(
        status='Pending'
    ).order_by(
        'date'
    )

    order_queue = deque(
        pending_orders
    )

    if order_queue:

        next_order = order_queue.popleft()

        next_order.status = 'Processing'

        next_order.save()

        messages.success(
            request,
            f'Order #{next_order.order_id} moved to Processing.'
        )

    else:

        messages.info(
            request,
            'No pending orders in queue.'
        )

    return redirect('orders')


# ============================================================
# INVENTORY HISTORY
# ============================================================

def inventory_history(request):

    transactions = StockTransaction.objects.select_related(
        'product'
    ).order_by(
        '-timestamp'
    )

    return render(
        request,
        'inventory_history.html',
        {
            'transactions': transactions
        }
    )


# ============================================================
# ALERTS
# ============================================================

def alerts(request):

    products = Product.objects.all()

    for product in products:

        if product.quantity == 0:

            Alert.objects.get_or_create(

                product=product,

                alert_type='Out of Stock',

                status='Unread',

                defaults={
                    'message':
                    f'{product.product_name} is out of stock.'
                }

            )

        elif product.quantity < product.minimum_stock:

            Alert.objects.get_or_create(

                product=product,

                alert_type='Low Stock',

                status='Unread',

                defaults={
                    'message':
                    f'{product.product_name} is low on stock.'
                }

            )

    alert_list = Alert.objects.select_related(
        'product'
    ).order_by(
        '-timestamp'
    )

    return render(
        request,
        'alerts.html',
        {
            'alerts': alert_list
        }
    )


# ============================================================
# MARK ALERT READ
# ============================================================

def mark_alert_read(request, alert_id):

    alert = get_object_or_404(
        Alert,
        alert_id=alert_id
    )

    alert.status = 'Read'

    alert.save()

    return redirect('alerts')


# ============================================================
# RESOLVE ALERT
# ============================================================

def resolve_alert(request, alert_id):

    alert = get_object_or_404(
        Alert,
        alert_id=alert_id
    )

    alert.status = 'Resolved'

    alert.save()

    return redirect('alerts')


# ============================================================
# REPORTS
# ============================================================

def reports(request):

    products = Product.objects.all()

    transactions = StockTransaction.objects.select_related(
        'product'
    ).order_by(
        '-timestamp'
    )

    orders_list = Order.objects.select_related(
        'product'
    ).order_by(
        '-date'
    )

    total_products = products.count()

    low_stock = products.filter(
        quantity__gt=0
    ).filter(
        quantity__lt=__import__('django').db.models.F('minimum_stock')
    ).count()

    out_of_stock = products.filter(
        quantity=0
    ).count()

    total_transactions = transactions.count()

    context = {

        'products': products,

        'transactions': transactions,

        'orders': orders_list,

        'total_products': total_products,

        'low_stock': low_stock,

        'out_of_stock': out_of_stock,

        'total_transactions': total_transactions,

    }

    return render(
        request,
        'reports.html',
        context
    )


# ============================================================
# ANALYTICS
# ============================================================

def analytics(request):

    products = Product.objects.all()

    total_stock = products.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    low_stock = products.filter(
        quantity__gt=0
    ).filter(
        quantity__lt=__import__('django').db.models.F('minimum_stock')
    ).count()

    out_of_stock = products.filter(
        quantity=0
    ).count()

    in_stock = products.filter(
        quantity__gte=__import__('django').db.models.F('minimum_stock')
    ).count()

    stock_in_total = StockTransaction.objects.filter(
        transaction_type='Stock In'
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    stock_out_total = StockTransaction.objects.filter(
        transaction_type='Stock Out'
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    order_statistics = Order.objects.values(
        'status'
    ).annotate(
        total=Count('order_id')
    )

    context = {

        'total_stock': total_stock,

        'low_stock': low_stock,

        'out_of_stock': out_of_stock,

        'in_stock': in_stock,

        'stock_in_total': stock_in_total,

        'stock_out_total': stock_out_total,

        'order_statistics': order_statistics,

    }

    return render(
        request,
        'analytics.html',
        context
    )