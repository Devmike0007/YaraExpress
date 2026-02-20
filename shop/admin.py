from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django import forms

from .models import Category, Product, Ingredient
from . import utils


class ImportForm(forms.Form):
	text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}),
						   help_text="Ex: Poivrons: 200, 300, 500\nUne ligne par produit ou groupe de variantes.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['titre']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['titre', 'prix', 'stock', 'category']
	search_fields = ['titre']

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('import-text/', self.admin_site.admin_view(self.import_products_view), name='shop_product_import_text'),
		]
		return custom_urls + urls

	def import_products_view(self, request):
		if request.method == 'POST':
			form = ImportForm(request.POST)
			if form.is_valid():
				text = form.cleaned_data['text']
				results = utils.parse_and_create_products(text)
				created = results.get('created', [])
				errors = results.get('errors', [])
				if created:
					messages.success(request, f"{len(created)} produit(s) créés avec succès.")
				if errors:
					for err in errors:
						messages.error(request, err)
				return redirect('..')
		else:
			form = ImportForm()

		context = {
			**self.admin_site.each_context(request),
			'form': form,
			'title': 'Importer des produits depuis du texte',
		}
		return render(request, 'admin/import_products.html', context)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
	list_display = ['nom', 'prix', 'is_active', 'date_creation']
	list_filter = ['is_active', 'date_creation']
	search_fields = ['nom']
	list_editable = ['is_active']
	
