from django.db import migrations

def set_cartitem_cart(apps, schema_editor):
    CartItem = apps.get_model('cart', 'CartItem')
    Cart = apps.get_model('cart', 'Cart')
    
    # You can assign a default cart for all CartItems with null cart, e.g., the first cart of the user
    for cart_item in CartItem.objects.filter(cart__isnull=True):
        cart_item.cart = Cart.objects.first()  # Assigning the first cart as default (adjust logic if needed)
        cart_item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_alter_cartitem_cart'),
    ]

    operations = [
        migrations.RunPython(set_cartitem_cart),
    ]
