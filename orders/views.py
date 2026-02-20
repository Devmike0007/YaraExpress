from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from shop.models import Product, Ingredient
from .models import Cart, CartItem, Order, OrderItem
from django.conf import settings
from urllib.parse import quote

def get_or_create_cart(user):
    """Obtient ou crée un panier pour l'utilisateur"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart
                                    
@login_required
def panier(request):
    """Affiche le panier de l'utilisateur"""
    cart = get_or_create_cart(request.user)
    ingredients = Ingredient.objects.filter(is_active=True)  # Charger tous les ingrédients actifs
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
        'all_ingredients': ingredients,  # Ajouter les ingrédients au contexte
    }
    return render(request, 'cart.html', context)

@login_required
@require_POST
def ajouter_au_panier(request, product_id):
    """Ajoute un produit au panier ou augmente sa quantité"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request.user)
    quantity = int(request.POST.get('quantity', 1))

    # Si le produit est déjà dans le panier, augmenter la quantité
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Retourner JSON si c'est une requête AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.titre} ajouté au panier',
            'cart_total': str(cart.get_total_price()),
            'cart_items': cart.get_total_items(),
        })

    return redirect('panier')

@login_required
@require_POST
def supprimer_du_panier(request, item_id):
    """Supprime un article du panier"""
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Article supprimé du panier',
            'cart_total': str(cart.get_total_price()),
            'cart_items': cart.get_total_items(),
        })

    return redirect('panier')

@login_required
@require_POST
def mettre_a_jour_panier(request, item_id):
    """Met à jour la quantité d'un article du panier"""
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Panier mis à jour',
            'item_total': str(cart_item.get_total_price()),
            'cart_total': str(cart.get_total_price()),
            'cart_items': cart.get_total_items(),
        })

    return redirect('panier')

@login_required
@require_POST
def add_ingredients_to_item(request, item_id):
    """Ajoute des ingrédients à un article du panier"""
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    ingredient_ids = request.POST.getlist('ingredient_ids')
    # Supprimer les ingrédients actuels et en ajouter de nouveaux
    cart_item.ingredients.clear()
    if ingredient_ids:
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids, is_active=True)
        cart_item.ingredients.set(ingredients)
    
    # Rediriger vers le panier
    return redirect('panier')

@login_required
def vider_panier(request):
    """Vide complètement le panier"""
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    return redirect('panier')

@login_required
def commander(request):
    """Crée une commande à partir du panier"""
    cart = get_or_create_cart(request.user)
    
    if not cart.items.exists():
        return redirect('panier')

    # Créer la commande
    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price()
    )

    # Ajouter les articles de la commande
    for cart_item in cart.items.all():
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.prix
        )
        # Copier les ingrédients du CartItem vers OrderItem
        order_item.ingredients.set(cart_item.ingredients.all())

    # Vider le panier
    cart.items.all().delete()

    return redirect('confirmation_commande', order_id=order.id)

@login_required
def confirmation_commande(request, order_id):
    """Affiche la confirmation de la commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'order_confirmation.html', context)


@login_required
def whatsapp_cart(request):
    """Compose un message WhatsApp depuis le panier et redirige vers wa.me"""
    cart = get_or_create_cart(request.user)
    if not cart.items.exists():
        return redirect('panier')
    # Récupère note optionnelle passée en querystring
    note = request.GET.get('note', '').strip()

    # Client
    name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    contact = request.user.email or 'Non renseigné'

    lines = [
        "🛒 Nouvelle commande — Yara Express",
        "",
        f"👤 Client: {name}",
        f"✉️ Email: {contact}",
        "",
        "🧾 Détails de la commande:",
    ]

    for item in cart.items.all():
        # appeler la méthode get_total_price() et formater
        try:
            line_price = f"{item.get_total_price():.2f}"
        except Exception:
            line_price = str(item.get_total_price())
        lines.append(f"• {item.product.titre} x {item.quantity} — {line_price} $")
        
        # Ajouter les ingrédients si disponibles
        if item.ingredients.exists():
            for ing in item.ingredients.all():
                try:
                    ing_price = f"{ing.prix:.2f}"
                except Exception:
                    ing_price = str(ing.prix)
                lines.append(f"  └ {ing.nom} +{ing_price} $")

    lines.append("")
    try:
        total = f"{cart.get_total_price():.2f}"
    except Exception:
        total = str(cart.get_total_price())
    lines.append(f"💵 Total: {total} $")
    if note:
        lines.append("")
        lines.append(f"📝 Note client: {note}")

    lines.append("")
    lines.append("Merci — Yara Express 🇨🇩")

    message = "\\n".join(lines)
    text = quote(message)
    numero = getattr(settings, 'WHATSAPP_NUMBER', '243975732060')
    url = f"https://wa.me/{numero}?text={text}"
    return redirect(url)


@login_required
def whatsapp_order(request, order_id):
    """Compose un message WhatsApp depuis une commande existante et redirige vers wa.me"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    lines = [
        "✅ Confirmation de commande — Yara Express",
        "",
        f"🧾 Commande #{order.id}",
        f"📅 Date: {order.created_at.strftime('%d/%m/%Y %H:%M')}",
        "",
        "Articles:",
    ]

    for item in order.items.all():
        try:
            line_price = f"{item.get_total_price():.2f}"
        except Exception:
            line_price = str(item.get_total_price())
        lines.append(f"• {item.product.titre} x {item.quantity} — {line_price} $")
        
        # Ajouter les ingrédients si disponibles
        if item.ingredients.exists():
            for ing in item.ingredients.all():
                try:
                    ing_price = f"{ing.prix:.2f}"
                except Exception:
                    ing_price = str(ing.prix)
                lines.append(f"  └ {ing.nom} +{ing_price} $")

    lines.append("")
    try:
        order_total = f"{order.total_price:.2f}"
    except Exception:
        order_total = str(order.total_price)
    lines.append(f"💵 Total: {order_total} $")
    lines.append("")
    lines.append("Merci pour votre confiance — Yara Express 🇨🇩")

    message = "\\n".join(lines)
    text = quote(message)
    numero = getattr(settings, 'WHATSAPP_NUMBER', '243975732060')
    url = f"https://wa.me/{numero}?text={text}"
    return redirect(url)
