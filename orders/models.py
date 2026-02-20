from django.db import models
from django.contrib.auth.models import User
from shop.models import Product, Ingredient


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        """Retourne le prix total du panier"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        """Retourne le nombre total d'articles dans le panier"""
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.username}"

    class Meta:
        verbose_name_plural = "Paniers"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='cart_items')

    def get_total_price(self):
        """Retourne le prix total pour cet article (prix produit + ingrédients) * quantité"""
        ingredient_price = sum(ing.prix for ing in self.ingredients.all())
        return (self.product.prix + ingredient_price) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.titre} dans le panier de {self.cart.user.username}"

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name_plural = "Articles du panier"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Commande #{self.id} de {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='order_items')

    def get_total_price(self):
        """Retourne le prix total: (prix du produit + prix des ingrédients) * quantité"""
        ingredient_price = sum(ing.prix for ing in self.ingredients.all())
        return (self.price + ingredient_price) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.titre}"
    
    class Meta:
        verbose_name_plural = "Articles de commande"
