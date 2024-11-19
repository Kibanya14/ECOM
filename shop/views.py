from django.shortcuts import redirect, render, get_object_or_404 
from .models import Product, Category, Commande
from django.core.paginator import Paginator
from django_countries import countries
from django.contrib.admin.views.decorators import staff_member_required
import json


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
            items=items,
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
        return redirect('confirmation')

    return render(request, 'shop/checkout.html', {'countries': countries})

def confimation(request):
    info = Commande.objects.all()[:1]
    for item in info:
        name = item.nom
    return render(request, 'shop/confirmation.html', {'name': name}) 


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
