from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm  # type: ignore
from .models import CustomUser , ColocationOffer , House
from django.contrib.auth import login , authenticate # type: ignore
from django_countries.widgets import CountrySelectWidget # type: ignore



class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'placeholder' : 'Entrez votre username'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'placeholder' : 'Entrez votre adresse email'})
    )
    STATUS_CHOICES = [
    ('Étudiant', 'Étudiant'),
    ('Entrepreneur', 'Entrepreneur'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Status",
        widget=forms.Select(attrs={'placeholder': 'Choisissez votre statut'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
        'placeholder' : 'Entrez votre mot de passe',
    }))
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
        'placeholder' : 'Entrez votre mot de passe'
    }))

    class Meta:
        model = CustomUser
        fields = ('username', 'email' , 'status', 'password1', 'password2')

class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = [
            'username','first_name', 'last_name', 'email', 'pays', 'date_naissance',
            'ville', 'adress', 'code_postal', 'phone_number',
            'genre', 'status'
        ]
        widgets = {
            'username' : forms.TextInput(),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pays': CountrySelectWidget(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'adress': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user and user.status != 'Admin':
            self.fields['status'].choices = [
                ('Etudiant', 'Etudiant'),
                ('Entrepreneur', 'Entrepreneur'),
            ]

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = [
            'title', 'description', 'property_type', 'furnished',
            'surface', 'rooms', 'bedrooms', 'address', 'city',
            'code_postal', 'region', 'location_name',
            'parking', 'elevator', 'balcony', 'heating', 'ac', 'garden'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la maison'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'furnished': forms.Select(attrs={'class': 'form-select'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Surface en m²'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de pièces'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de chambres'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'code_postal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Code postal'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la localisation'}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'heating': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ColocationOfferForm(forms.ModelForm):
    class Meta:
        model = ColocationOffer
        fields = ['house', 'nombre_personne', 'rent', 'charges', 'autorisation']
        widgets = {
            'house': forms.Select(attrs={'class': 'form-select'}),
            'nombre_personne': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de personne'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Loyer mensuel'}),
            'charges': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Charges mensuelles'}),
            'autorisation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['house'].queryset = House.objects.filter(owner=user)
