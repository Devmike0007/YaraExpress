from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ['user', 'created_at', 'get_total_price']
	list_filter = ['created_at']
	search_fields = ['user__username', 'user__email']
	readonly_fields = ['created_at', 'updated_at']


class CartItemInline(admin.TabularInline):
	model = CartItem
	raw_id_fields = ['product']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ['cart', 'product', 'quantity', 'get_total_price']
	list_filter = ['added_at']
	search_fields = ['cart__user__username', 'product__titre']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'user', 'status', 'total_price', 'created_at']
	list_filter = ['status', 'created_at']
	search_fields = ['user__username', 'user__email']
	readonly_fields = ['total_price', 'created_at', 'updated_at']
	ordering = ['-created_at']
	fieldsets = (
		('Informations client', {
			'fields': ('user',)
		}),
		('Statut', {
			'fields': ('status',)
		}),
		('Détails', {
			'fields': ('total_price', 'created_at', 'updated_at')
		}),
	)


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	raw_id_fields = ['product']
	readonly_fields = ['price', 'get_total_price']
	extra = 0
	filter_horizontal = ['ingredients']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ['order', 'product', 'quantity', 'price', 'get_total_price', 'get_ingredients']
	list_filter = ['order__created_at']
	search_fields = ['order__id', 'product__titre']
	filter_horizontal = ['ingredients']
	
	def get_ingredients(self, obj):
		"""Affiche la liste des ingrédients pour cet article"""
		ingredients = obj.ingredients.all()
		return ', '.join([f"{ing.nom} (+{ing.prix}$)" for ing in ingredients]) if ingredients.exists() else "Aucun"
	get_ingredients.short_description = "Ingrédients"
