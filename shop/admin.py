from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, Product, Commande
import json

admin.site.site_header = "Administration Manga Store"
admin.site.site_title = "Manga Store Admin"
admin.site.index_title = "Tableau de bord"
 
@admin.register(Category)
class AdminCategorie(admin.ModelAdmin):
    list_display = ('name', 'date_added')
    search_fields = ('name',)
    ordering = ('-date_added',)

@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'rating_display', 'discount_percentage', 'image_preview', 'date_added')
    list_filter = ('category', 'date_added')
    search_fields = ('title', 'description')
    list_editable = ('price', 'discount_percentage')
    readonly_fields = ('date_added', 'image_preview')

    def rating_display(self, obj):
        stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html('<span style="color: #FFD700;">{}</span>', stars)
    rating_display.short_description = 'Note'

    def image_preview(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html(f'<img src="{image_url}" width="50" height="50" style="object-fit: cover;" />')
        return "Aucune image"
    image_preview.short_description = 'Aperçu'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'price', 'category')
        }),
        ('Image', {
            'fields': ('image', 'image_url', 'image_preview'),
            'description': "Choisissez une image à uploader ou fournissez une URL d'image."
        }),
        ('Avis et réduction', {
            'fields': ('rating', 'number_of_reviews', 'discount_percentage'),
            'classes': ('collapse',)
        }),
        ('Informations supplémentaires', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Editing an existing object
            fieldsets[1][1]['fields'] = ('image', 'image_url', 'image_preview')
        else:  # Adding a new object
            fieldsets[1][1]['fields'] = ('image', 'image_url')
        return fieldsets

@admin.register(Commande)
class AdminCommande(admin.ModelAdmin):
    list_display = ('nom', 'email', 'address', 'ville', 'pays', 'total', 'telephone', 'date_commande', 'display_items')
    list_filter = ('pays', 'date_commande')
    search_fields = ('nom', 'email', 'address')
    readonly_fields = ('date_commande', 'display_items_detail')

    def display_items(self, obj):
        try:
            items = json.loads(obj.items)
            return format_html('<br>'.join([f"{item[1]} (x{item[0]})" for item in items.values()]))
        except json.JSONDecodeError:
            return "Erreur de décodage JSON"
    display_items.short_description = 'Articles commandés'

    def display_items_detail(self, obj):
        try:
            items = json.loads(obj.items)
            items_html = ['<div class="flex flex-col space-y-2">']
            for item in items.values():
                items_html.append(f'''
                    <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
                        <span class="font-semibold">{item[1]}</span>
                        <span class="bg-blue-500 text-white px-2 py-1 rounded">Qté: {item[0]}</span>
                        <span class="bg-green-500 text-white px-2 py-1 rounded">${item[2]}</span>
                    </div>
                ''')
            items_html.append('</div>')
            return format_html(''.join(items_html))
        except json.JSONDecodeError:
            return "Erreur de décodage JSON"
    display_items_detail.short_description = 'Détails des articles'

    fieldsets = (
        ('Informations client', {
            'fields': ('nom', 'email', 'telephone', 'address', 'ville', 'pays')
        }),
        ('Détails de la commande', {
            'fields': ('total', 'date_commande', 'display_items_detail')
        }),
    )

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',)
        }