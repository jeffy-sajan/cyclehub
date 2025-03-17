from django.shortcuts import render, get_object_or_404,redirect
from .models import Category,Product
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from django.utils.crypto import get_random_string
from django.urls import reverse


def home(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'home.html', context)

# View for listing products within a specific category

def products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    context = {'category': category, 'products': products}
    return render(request, 'products.html', context)


def register(request):
    if request.method == 'POST':
        # Get form values
        username = request.POST.get('u', '').strip()
        password = request.POST.get('p', '').strip()
        confirm_password = request.POST.get('cp', '').strip()
        email = request.POST.get('e', '').strip()

        # Validation checks
        if not username or not password or not confirm_password or not email:
            messages.error(request, 'All fields are required', extra_tags='register')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long', extra_tags='register')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match', extra_tags='register')
        elif not email.endswith('@gmail.com'):  # Replace with your domain or remove if not required
            messages.error(request, 'Enter a valid email address', extra_tags='register')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists', extra_tags='register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered', extra_tags='register')
        else:
            # Create the new user
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            # Automatically log in the user after registration
            login(request, user)
            messages.success(request, 'Registration successful', extra_tags='register')
            return redirect('cycle:login')  

    return render(request, 'register.html')



 

def user_login(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validate input fields
        if not email_or_username or not password:
            messages.error(request, "Email/Username and password are required", extra_tags='login')
            return redirect('cycle:login')

        # Check if input is an email or username
        try:
            if '@' in email_or_username and not email_or_username == 'admin':  # Treat as email unless it's 'admin'
                user_obj = User.objects.get(email=email_or_username)
                username = user_obj.username  # Retrieve username from email
            else:  # Treat as username
                username = email_or_username
        except User.DoesNotExist:
            messages.error(request, "Invalid email/username or password", extra_tags='login')
            return redirect('cycle:login')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.get_messages(request)  # Clear all old messages

            # Redirect superusers or staff to the admin panel
            if user.is_superuser or user.is_staff:
                return redirect(reverse('admin:index'))  # Django admin URL

            return redirect('cycle:home')  # Redirect to home page after login
        else:
            messages.error(request, "Invalid email/username or password", extra_tags='login')

    return render(request, 'login.html')




def user_logout(request):
    logout(request)
    request.session.flush()  # Clear the session completely
    messages.success(request, "Successfully logged out",extra_tags='logout')
    return redirect('cycle:home')  # Redirect to the home page after logout


def details(request, product_id):
    # Retrieve the specific product using its ID
    product = get_object_or_404(Product, id=product_id)
    
    # Pass the product to the template
    return render(request, 'details.html', {'product': product})




@login_required
def profile_view(request):
    # Try to get the user's profile, or create one if it doesn't exist
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create a new UserProfile if one doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('cycle:view')  # Redirect to the profile page after updating
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile_view.html', {'user_profile': user_profile, 'form': form})


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            # Generate a new random password
            new_password = get_random_string(length=10)  # Adjust length as needed
            user.set_password(new_password)
            user.save()
            # Display the new password on the screen
            return render(request, 'password_reset_confirmation.html', {'new_password': new_password})
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    return render(request, 'forgot_password.html')


 

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)  # Search by product name

    return render(request, 'search_results.html', {
        'products': products,
        'query': query,
    })
