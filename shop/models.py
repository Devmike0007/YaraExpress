from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titre']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.titre

class Product(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    date_publication = models.DateTimeField(auto_now_add=True)
    data_modification_pub = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_publication']
    def __str__(self):
        return self.titre
    

class Ingredient(models.Model):
    """Modèle pour les ingrédients supplémentaires"""
    nom = models.CharField(max_length=100, unique=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom']
        verbose_name_plural = "Ingrédients"

    def __str__(self):
        return f"{self.nom} ({self.prix}$)"
    