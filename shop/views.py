from django.shortcuts import redirect, render, get_object_or_404 
from .models import Product, Category, Commande
from django.core.paginator import Paginator
from django_countries import countries
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


def index(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    item_nom = request.GET.get('item-nom')
    
    product_objects = Product.objects.all()
    selected_category = None
    category_empty = False
    
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        product_objects = product_objects.filter(category=selected_category)
        if not product_objects.exists():
            category_empty = True
    
    if item_nom and item_nom != '':
        product_objects = product_objects.filter(title__icontains=item_nom)
    
    if not category_empty:
        paginator = Paginator(product_objects, 8)  # 8 products per page
        page = request.GET.get('page')
        product_objects = paginator.get_page(page)
        
        # Set image_src for each product
        for product in product_objects:
            product.image_src = product.get_image_url()
    else:
        product_objects = []
    
    context = {
        'product_objects': product_objects,
        'categories': categories,
        'selected_category': selected_category,
        'category_empty': category_empty
    }
    
    return render(request, 'shop/index.html', context)

def about(request):
    return render(request, 'shop/about.html')

def detail(request, myid):
    product_object = get_object_or_404(Product, id=myid)
    return render(request, 'shop/detail.html', {'product': product_object})

def checkout(request):
    if request.method == "POST":
        items = request.POST.get('items')
        total = request.POST.get('total')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        code_pays = request.POST.get('code_pays')
        telephone = request.POST.get('telephone')
        address = request.POST.get('address')
        ville = request.POST.get('ville')
        pays = request.POST.get('pays')

        # Valider le numéro de téléphone
        if not telephone.isdigit() or len(telephone) < 9 or len(telephone) > 15:
            return render(request, 'shop/checkout.html', {
                'error_message': 'Le numéro de téléphone doit contenir entre 9 et 15 chiffres.',
                'countries': countries
            })

        # Créer une nouvelle instance de la commande
        com = Commande(
            total=total,
            nom=nom,
            email=email,
            code_pays=code_pays,
            telephone=telephone,
            address=address,
            ville=ville,
            pays=pays
        )
        com.save()

        # Ajoutez les produits à la commande (vous devez avoir une logique pour récupérer les IDs des produits)
        product_ids = json.loads(items)  # Supposons que vous stockez les IDs des produits dans `items`
        for product_id in product_ids:
            product = get_object_or_404(Product, id=product_id)
            com.produits.add(product)

        return redirect('confirmation', order_id=com.id)  # Redirigez vers la confirmation avec l'ID de la commande

    return render(request, 'shop/checkout.html', {'countries': countries})

def confirmation(request, order_id):
    # Récupérer la commande spécifique par ID
    commande = get_object_or_404(Commande, id=order_id)

    # Récupérer les informations de la commande
    name = commande.nom
    products = commande.produits.all()  # Récupérer tous les produits associés à cette commande

    # Calculer le total pour chaque produit et le total général
    product_details = []
    total_amount = 0

    for product in products:
        quantity = 1  # Remplacez ceci par la quantité réelle si disponible
        total_price = product.price * quantity
        product_details.append({
            'title': product.title,
            'price': product.price,
            'quantity': quantity,
            'total_price': total_price,
        })
        total_amount += total_price

    context = {
        'name': name,
        'products': product_details,
        'order': commande,
        'total_amount': total_amount,
    }

    return render(request, 'shop/confirmation.html', context)

def download_invoice(request, order_id):
    # Récupérer la commande spécifique par ID
    commande = get_object_or_404(Commande, id=order_id)
    products = commande.produits.all()  # Récupérer tous les produits associés à cette commande

    # Créer une liste de détails des produits avec le prix total
    product_details = []
    for product in products:
        quantity = 1  # Remplacez ceci par la quantité réelle si disponible
        total_price = product.price * quantity
        product_details.append({
            'title': product.title,
            'price': product.price,
            'quantity': quantity,
            'total_price': total_price,
        })

    # Créer un template pour le PDF
    html_string = render_to_string('shop/invoice.html', {'order': commande, 'products': product_details})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{commande.id}.pdf"'
    return response


from .models import Testimonial
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def forum(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Validation simple
        errors = {}
        if not name:
            errors['name'] = "Le nom est requis."
        if not email:
            errors['email'] = "L'email est requis."
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = "L'email n'est pas valide."
        if not message:
            errors['message'] = "Le message est requis."
        
        if not errors:
            Testimonial.objects.create(name=name, email=email, message=message)
            return redirect('forum')
        else:
            return render(request, 'forum.html', {
                'testimonials': testimonials,
                'errors': errors,
                'name': name,
                'email': email,
                'message': message
            })
    
    return render(request, 'shop/forum.html', {'testimonials': testimonials})
