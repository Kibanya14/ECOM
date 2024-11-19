from django.db import models
from django.db.models.fields.related import ForeignKey
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField
import requests

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']
        verbose_name_plural = "Categories"  # Correction de l'orthographe

    def __str__(self):
        return self.name    

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    category = ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=10000, blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    number_of_reviews = models.IntegerField(default=0)
    discount_percentage = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage de réduction appliqué pour les achats en quantité"
    )

    def get_discounted_price(self, quantity):
        if quantity > 1:
            discount = self.price * (self.discount_percentage / 100) * (quantity - 1)
            return max(self.price - discount, 0)
        return self.price

    def display_rating(self):
        return f"{self.rating:.1f}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            if 'google.com/url' in self.image_url:
                try:
                    response = requests.get(self.image_url, allow_redirects=False)
                    if response.status_code == 302:
                        return response.headers['Location']
                except:
                    pass
            return self.image_url
        return None

    class Meta:
        ordering = ['-date_added']  

    def __str__(self):
        return self.title         
class Commande(models.Model):
    items = models.CharField(max_length=300)
    total = models.CharField(max_length=200)
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    code_pays = models.CharField(max_length=5, verbose_name="Code pays")
    telephone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\d{9,15}$',
                message='Le numéro de téléphone doit contenir entre 9 et 15 chiffres.'
            )
        ],
        verbose_name="Numéro de téléphone"
    )
    address = models.CharField(max_length=200)
    ville = models.CharField(max_length=200)
    pays = CountryField()
    date_commande = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_commande']

    def __str__(self):
        return f"{self.nom} - {self.date_commande}"

    @property
    def numero_complet(self):
        return f"{self.code_pays}{self.telephone}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)