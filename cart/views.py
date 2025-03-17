from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import CartItem, Order,OrderItem
from cycle.models import Product 
from django.contrib import messages
from django.http import HttpResponseBadRequest
from cycle.models import UserProfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the product is in stock
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('product_details', product_id=product_id)

    # Link cart item to logged-in user
    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user,  # Associate item with the current user
    )

    # If the item already exists in the cart, increase the quantity
    if not created:
        if cart_item.quantity < product.stock:  # Ensure we don't exceed the available stock
            cart_item.quantity += 1
        else:
            messages.error(request, f"Only {product.stock} units of {product.name} are available.")
            return redirect('cycle:details', product_id=product_id)
    cart_item.save()

    messages.success(request, f"{product.name} has been added to your cart.")
    return redirect('cart:view_cart')



@login_required
def view_cart(request):
    # Fetch the user's cart items
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        # Handle case where cart is empty
        return render(request, 'cart.html', {'cart_items': cart_items, 'total_cost': 0})
    
    # Recalculate the total cost
    total_cost = sum(item.total_price for item in cart_items)
    
    # Optionally, you could check stock availability or update the cart if needed
    # You can access stock directly in the template, but if you need to adjust it in the view:
    for item in cart_items:
        if item.quantity > item.product.stock:
            # Here you could apply logic to handle exceeding stock or display a message
            item.out_of_stock = True
        else:
            item.out_of_stock = False
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_cost': total_cost})



from django.contrib import messages

@login_required
def update_cart_item(request, cart_item_id, action):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    product = cart_item.product

    if action == 'increase':
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Quantity increased to {cart_item.quantity}")
        else:
            # Add a custom tag to indicate this is a cart-specific error
            messages.add_message(request, messages.ERROR, f"Cannot increase quantity. Only {product.stock} items in stock.", extra_tags='cart_error')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Quantity decreased to {cart_item.quantity}")
        else:
            messages.error(request, "Minimum quantity is 1.")
    return redirect('cart:view_cart')





# Remove Cart Item
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    
    return redirect('cart:view_cart')




import re
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cycle.models import UserProfile
from cart.models import CartItem, Order, OrderItem



@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    error_message = None  # Variable to store error message

    if request.method == 'POST':
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        phone_number = request.POST.get('phone-number')
        payment_method = request.POST.get('payment-method')

        # Validation
        if not address or not pincode or not phone_number or not payment_method:
            error_message = "All fields are required"
        elif not re.match(r'^\d{6}$', pincode):
            error_message = "Invalid pincode. It should be a 6-digit number."
        elif not re.match(r'^\d{10}$', phone_number):
            error_message = "Invalid phone number. It should be a 10-digit number."


        if error_message:
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'user_profile': user_profile,
                'error_message': error_message  # Pass error message to template
            })

        # Create an Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            pincode=pincode,
            phone_number=phone_number,
            payment_method=payment_method,
            total_price=total_price
        )

        for item in cart_items:
            # Deduct stock for each product
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                return render(request, 'checkout.html', {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'user_profile': user_profile,
                    'error_message': f"Not enough stock for {product.name}"
                })

            # Create OrderItems
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the cart
        cart_items.delete()

        return redirect('cart:order_confirmation')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_profile': user_profile
    })





@login_required
def order_confirmation(request):

    return render(request, 'order_confirmation.html')


@login_required
def orders_view(request):
    # Fetch all orders for the logged-in user
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been successfully cancelled.")
    else:
        messages.error(request, f"Order #{order.id} cannot be cancelled.")

    return redirect('cart:orders')  # Redirect to the orders page



 

def generate_pdf(request, order_id):
    # Fetch data for the PDF
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total_price = sum(item.quantity * item.price for item in order.items.all())

    # Render HTML template with context
    context = {'order': order, 'total_price': total_price}
    html_content = render_to_string('pdf_template.html', context)

    # Create a response object for the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Convert HTML to PDF
    result = pisa.CreatePDF(html_content, dest=response)
    if result.err:
        return HttpResponse('Failed to generate PDF', status=500)

    return response
