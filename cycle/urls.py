"""
URL configuration for cyclehub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cycle import views

app_name='cycle'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('products/<int:category_id>/', views.products, name='products'),
    path('details/<int:product_id>/', views.details, name='details'),
    path('profile/', views.profile_view, name='view'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
        path('search/', views.search_products, name='search_products'),



    



]

