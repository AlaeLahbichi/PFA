from django.contrib.auth.models import AbstractUser # type: ignore
from django.conf import settings # type: ignore
from django.db import models # type: ignore
from django_countries.fields import CountryField # type: ignore
from django.utils import timezone # type: ignore
from django.utils.timezone import now


class CustomUser(AbstractUser):
    SEX_TYPES = [
        ('Homme' , 'Homme'),
        ('Femme' , 'Femme'),
    ]
    Status_Types = [
        ('Admin','Admin'),
        ('Visiteur','Visiteur'),
        ('Étudiant' , 'Étudiant'),
        ('Entrepreneur' , 'Entrepreneur') , 
    ]

    email = models.EmailField(unique=True)
    pays = CountryField(default='MA')
    date_naissance = models.DateField(blank=True , null= True )
    ville = models.CharField(max_length=255,blank=True,null=True)
    adress = models.CharField(max_length=255,blank=True,null=True)
    code_postal = models.BigIntegerField(blank=True,null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    genre = models.CharField(max_length=255,choices=SEX_TYPES,default="Homme")
    status = models.CharField(max_length=255,choices=Status_Types,default="Visiteur")
    ProfileImage = models.ImageField(upload_to="profileimage/" , default="profileimage/default.png")
    Email_Verifiyed = models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    activation = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

class Entrepreneur(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="entrepreneur"
    )
    societé = models.CharField(max_length=255,blank=True,null=True)
    société_id = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return self.user.username

class Etudiant(models.Model):
    niveau_choice = [
        ('Licence' , 'Licence') , 
        ('Master' , 'Master') , 
        ('Docotorat' , 'Doctorat')
    ]
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="etudiant"
    )
    universite = models.CharField(max_length=255,null=True,blank=True)
    niveau_scolaire = models.CharField(max_length=255,choices=niveau_choice,null=True,blank=True)
    bourse = models.BooleanField(default=False)
    montant_bourse = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    job_etudiant = models.BooleanField(default=False)
    job_etudiant_name = models.CharField(max_length=255,blank=True,null=True)
    job_etudiant_revenu = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    revenu_mensuel_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    def __str__(self):
        return self.user.username 

class City(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    region = models.CharField(max_length=100,blank=True,null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return self.name

class House(models.Model):
    PROPERTY_TYPES = [
        ('Appartement', 'Appartement'),
        ('Maison', 'Maison'),
        ('Studio', 'Studio'),
        ('Loft', 'Loft'),
        ('Chambre', 'Chambre'),
        ('Autre', 'Autre'),
    ]

    FURNISHED_CHOICES = [
        ('Meublé', 'Meublé'),
        ('Non meublé', 'Non meublé'),
    ]

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="houses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=255, choices=PROPERTY_TYPES)
    furnished = models.CharField(max_length=255, choices=FURNISHED_CHOICES)

    surface = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()

    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    code_postal = models.BigIntegerField(blank=True, null=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    location_name = models.CharField(max_length=255, default="Location undefined")

    parking = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    heating = models.BooleanField(default=False)
    ac = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.city}"

class ColocationOffer(models.Model):
    STATUS_TYPES = [
        ('Disponible', 'Disponible'),
        ('Refusé', 'Refusé'),
        ('En attente', 'En attente'),
        ('Fini', 'Fini'),
    ]

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="colocation_offers")
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True , blank=True , related_name="offers")
    
    nombre_personne = models.PositiveIntegerField(default=1)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    charges = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=255, choices=STATUS_TYPES, default="En attente")
    autorisation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.house.title} - {self.status}"
 
class ColocationPhoto(models.Model):
    offer = models.ForeignKey(ColocationOffer, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='colocation_photos/')

    def __str__(self):
        return f"Photo de {self.offer.house.title}"

class Like_Offer(models.Model):
    offer = models.ForeignKey('ColocationOffer', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='liked_offers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('offer', 'user') 

    def __str__(self):
        return f"{self.user} aime {self.offer}"
    
class Thread(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thread_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='thread_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Thread entre {self.user1.username} et {self.user2.username}"
    
    def get_other_user(self, current_user):
        if self.user1 == current_user:
            return self.user2
        elif self.user2 == current_user:
            return self.user1
        else:
            return None

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.sender.username} dans {self.thread}"

    class Meta:
        ordering = ['timestamp']  

class Candidature(models.Model):
    status_choice = [
        ('EN ATTENTE' , 'EN ATTENTE') , 
        ('APPROUVÉE' , 'APPROUVÉE'), 
        ('REFUSÉE' , 'REFUSÉE')
    ]
    owner = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="owner")
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="sender")
    offre = models.ForeignKey(ColocationOffer , on_delete=models.CASCADE , blank=True , null=True , related_name="offre")
    status = models.CharField(max_length=255,choices=status_choice,default="EN ATTENTE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidature de {self.sender.username} à {self.owner.username}"

class Réglamation(models.Model):
    status_choice = [
        ('En cours de traitement' , 'En cours de traitement') , 
        ('Rejetée' , 'Rejetée'), 
        ('Résolue' , 'Résolue')
    ]
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="réclameur")
    subject = models.CharField(max_length=255,blank=True,null=True)
    content = models.CharField(max_length=2000,null=True,blank=True)
    status = models.CharField(max_length=255,choices=status_choice,default="En cours de traitement")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réclamation de la part de f{self.sender.username}"

class Notification(models.Model):
    destinataire = models.ForeignKey(CustomUser , on_delete=models.CASCADE , related_name="user")
    message = models.CharField(max_length=1000,blank=True,null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"Notification pour {self.destinataire.email} - {self.message[:50]}"