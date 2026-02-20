import re
from decimal import Decimal
from django.db import transaction
from .models import Product, Category


def parse_line(line):
    """Parse une ligne du type 'Nom: 200, 300, 500' et retourne (name, [prices])"""
    if ':' in line:
        name_part, rest = line.split(':', 1)
        name = name_part.strip()
        nums = re.findall(r"\d+[\.,]?\d*", rest)
    else:
        # Si pas de :, on prend le premier mot comme nom et le reste comme prix
        parts = line.split()
        if not parts:
            return None, []
        name = parts[0]
        nums = re.findall(r"\d+[\.,]?\d*", line)

    prices = []
    for n in nums:
        n = n.replace(',', '.')
        try:
            prices.append(Decimal(n))
        except Exception:
            continue
    return name, prices


def parse_and_create_products(text, default_category='Importé', default_stock=100):
    """Analyse le texte et crée des produits.

    Retourne un dict {'created': [Product,...], 'errors': [str,...]}
    """
    created = []
    errors = []

    # ensure default category exists
    category, _ = Category.objects.get_or_create(titre=default_category)

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        errors.append('Le texte est vide.')
        return {'created': created, 'errors': errors}

    with transaction.atomic():
        for idx, line in enumerate(lines, start=1):
            name, prices = parse_line(line)
            if not name:
                errors.append(f'Ligne {idx}: nom introuvable.')
                continue
            if not prices:
                # si pas de prix, créer un produit sans prix (0.0)
                try:
                    p = Product.objects.create(titre=name, description='', prix=Decimal('0.0'), stock=default_stock, category=category)
                    created.append(p)
                except Exception as e:
                    errors.append(f'Ligne {idx} ({line}): erreur création produit: {e}')
                continue

            # créer une entrée par prix (ex: variantes taille/poids)
            for pr in prices:
                title = f"{name} {pr}"
                try:
                    p = Product.objects.create(titre=title, description='', prix=pr, stock=default_stock, category=category)
                    created.append(p)
                except Exception as e:
                    errors.append(f'Ligne {idx} ({title}): erreur création produit: {e}')

    return {'created': created, 'errors': errors}
