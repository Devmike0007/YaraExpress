from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Category, Ingredient
# Create your views here.
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "boutique.html", {"products": products, "categories": categories})

def about(request):
    return render(request, "appropos.html")
def recherche(request):
    query = request.GET.get('recherche')
    if query is None:
        query = ""
    products = Product.objects.filter(titre__icontains=query)
    return render(request, "search.html", {"query": query,"products": products})


def get_ingredients_api(request):
    """Retourne la liste des ingrédients actifs en JSON"""
    ingredients = Ingredient.objects.filter(is_active=True).values('id', 'nom', 'prix')
    return JsonResponse(list(ingredients), safe=False)