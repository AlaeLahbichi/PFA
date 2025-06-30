from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse # type: ignore
from .forms import CustomUserCreationForm , ColocationOfferForm , CustomUserUpdateForm , HouseForm
import time 
from django.db import IntegrityError # type: ignore
from django.core.mail import send_mail # type: ignore
from django.core.mail import EmailMultiAlternatives # type: ignore
from premailer import transform # type: ignore
from django.template.loader import render_to_string # type: ignore
from django.utils.html import strip_tags # type: ignore
from django.utils import timezone # type: ignore
from .models import CustomUser , ColocationOffer , ColocationPhoto , Etudiant , Like_Offer , City , House , Thread , Message , Candidature , Notification
from django.contrib import messages # type: ignore
from django.http import HttpResponse , Http404, HttpResponseRedirect # type: ignore
from django.contrib.auth import login , authenticate , logout  # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
import cv2 # type: ignore
import os
from django.conf import settings # type: ignore
from django.http import JsonResponse # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.contrib.auth.hashers import check_password , make_password # type: ignore
from django.core.paginator import Paginator # type: ignore
from django.db.models import Q # type: ignore
from django.http import JsonResponse # type: ignore
from datetime import date
from datetime import datetime
from .utils import get_device_info
import pytz # type: ignore
from django.db.models import Q




#Les fonctions qui retourne les pages (templates)
def verification_finish(request):
    return render(request,'base/verification_finish.html')

@login_required(login_url='/app1/login/')
def Home_Page(request):
    annonces = ColocationOffer.objects.filter(status = "Disponible")
    count = Notification.objects.filter(destinataire = request.user , is_read = False ).count()
    liked_offer = Like_Offer.objects.filter(user = request.user,offer__status = "Disponible").values_list('offer',flat=True)
    return render(request,'pages/home/home.html',{"annonces":annonces , "liked_offer" : liked_offer,"active":0,"count":count})

def Home_Page_Off(request):
    annonces = ColocationOffer.objects.filter(status = "Disponible")
    return render(request,'pages/home/home_off.html',{"annonces":annonces })

#Les fonctions relatives aux annonces
def annonce_page(request , code ):
    annonce = ColocationOffer.objects.get(id = code )
    images = ColocationPhoto.objects.filter(offer = annonce)
    annonce_similaire = ColocationOffer.objects.filter(house__city=annonce.house.city).exclude(id=annonce.id)[:3]
    return render(request,'pages/annonce.html',{"annonce":annonce , "images" : images , "similaire" : annonce_similaire})

@login_required(login_url='/app1/login/')
def ajouter_annonce_colocation(request):

    if request.user.status == "Visiteur":
        messages.error(request,"Impossible d'ajouter un bien immobilier car vous avez pas les droits nécessaires merci de nous contacter pour résoudre ce problème")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method == 'POST':
        form = ColocationOfferForm(request.POST , user=request.user)
        files = request.FILES.getlist('photos')
        if form.is_valid():
            annonce = form.save(commit=False)
            if ColocationOffer.objects.filter(owner=request.user, house=annonce.house).exclude(Q(status="Fini") | Q(status="Refusé")).exists():
                messages.error(request,"Impossible de partager beaucoup d'annonces actives pour le même bien")
                return redirect('homepage')
            annonce.owner = request.user
            annonce.save()
            for f in files:
                ColocationPhoto.objects.create(offer=annonce, image=f) 
            messages.success(request , "Ajout d'une annonce de colocation avec succés") 
            return redirect('homepage')
    else:
        form = ColocationOfferForm(user = request.user)
    return render(request, 'pages/add_annonce.html', {'form': form})

@login_required(login_url='/app1/login/')
def ajouter_house_action(request):

    if request.user.status == "Visiteur":
        messages.error(request,"Impossible d'ajouter un bien immobilier car vous avez pas les droits nécessaires merci de nous contacter pour résoudre ce problème")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            house = form.save(commit=False)
            house.owner = request.user
            house.code_postal = house.city.postal_code
            house.region = house.city.region
            similar_house = House.objects.filter(
                owner=request.user,
                title__iexact=house.title.strip(),
                address__iexact=house.address.strip(),
                city=house.city
            ).first()
            if similar_house:
                messages.error(request, "⚠️ Une maison similaire existe déjà dans votre liste.")
                return render(request, 'pages/add_house.html', {'form': form})
            house.save()
            messages.success(request,"Ajout avec succés du bien immobilier")
            return redirect('homepage')
    else:
        form = HouseForm()
    return render(request, 'pages/add_house.html', {'form': form})

def supprimer_annonce_admin(request, id):
    try:
        annonce = get_object_or_404(ColocationOffer, id=id)
        annonce.delete()
        messages.success(request, "La suppression de l'offre a été effectuée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de l'offre : {str(e)}")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def mes_annonces_page(request):
    annonces = ColocationOffer.objects.filter(owner = request.user.id)
    for x in annonces : 
        count = Candidature.objects.filter(offre = x , status = "EN ATTENTE").count()
        x.candidature_count = count 
    return render(request,'private/mes_annonces.html',{'annonces' : annonces})

def modifier_annonce(request,id):
    annonce = ColocationOffer.objects.get(id = id)
    return render(request,'private/modifier_annonce.html',{'annonce' : annonce , 'id' : id })

def supprimer_annonce(request,id):
    try :
        annonce =  get_object_or_404(ColocationOffer , id = id )
        annonce.delete()
        messages.success(request,"Suppression de l'annonce avec succés")
        return redirect('mes_annonces')
    
    except Exception as e :
        messages.error(request,"Une erreur s'est produite : " , e )
        return redirect('mes_annonces')

def modifier_annonce_action(request,id):
    if request.method == "POST":
        if request.POST.get('autorisation') == "on" : 
            try : 
                annonce = get_object_or_404(ColocationOffer , id = id)
                house = get_object_or_404(House , id = annonce.house.id)
                house.title = request.POST.get('title')
                house.description = request.POST.get('description')
                house.property_type = request.POST.get('property_type')
                house.furnished = request.POST.get('furnished')
                house.surface = request.POST.get('surface')
                house.rooms = request.POST.get('rooms')
                house.bedrooms = request.POST.get('bedrooms')
                house.address = request.POST.get('address')
                house.region = request.POST.get('region')
                house.code_postal = request.POST.get('code_postal')
                if request.POST.get('parking') == 'on' : 
                    house.parking = True
                elif request.POST.get('elevator') == 'on' : 
                    house.elevator = True 
                elif request.POST.get('balcony') == 'on' : 
                    house.balcony = True 
                elif request.POST.get('heating') == 'on' :
                    house.heating = True
                elif request.POST.get('ac') == 'ac' : 
                    house.ac = True 
                elif request.POST.get('garden') == 'garden' :
                    house.garden = True 
                annonce.status = request.POST.get('status')
                annonce.nombre_personne = request.POST.get('nombre_personne')
                annonce.rent = request.POST.get('rent')
                annonce.charges = request.POST.get('charges')
                house.save()
                annonce.save()
                messages.success(request,f'Modification avec succés de l\'annonce {annonce.id}')
                return redirect('mes_annonces')
            except Exception as e :
                messages.error(request,f'Impossible d\'éffectuer la modification , une erreur s\'est produite {e}')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else : 
            messages.error(request,'Merci de confirmer l\'autorisation de cette annonce')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else : 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def filter_colocation(request):
    if request.method == 'POST':

        property_type = request.POST.get('type')
        city = request.POST.get('city')
        min_price = request.POST.get('prix-min')
        max_price = request.POST.get('prix-max')
        bedrooms = request.POST.get('bedrooms')
        min_surface = request.POST.get('surface-min')
        max_surface = request.POST.get('surface-max')
        furnished = request.POST.get('furnished')
        gender = request.POST.get('genre')
        occupation = request.POST.get('status')
        garden = bool(request.POST.get('garden'))
        parking = bool(request.POST.get('parking'))
        balcony = bool(request.POST.get('balcony'))
        ac = bool(request.POST.get('ac'))
        elevator = bool(request.POST.get('elevator'))
        heating = bool(request.POST.get('heating'))
        queryset = ColocationOffer.objects.filter(status = "Disponible")

        if property_type and property_type != 'Tous':
            queryset = queryset.filter(house__property_type=property_type)
        
        if city:
            queryset = queryset.filter(house__city__name=city)
        
        if min_price:
            queryset = queryset.filter(rent__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(rent__lte=max_price)
        
        if bedrooms:
            queryset = queryset.filter(house__bedrooms=bedrooms)
        
        if min_surface:
            queryset = queryset.filter(house__surface__gte=min_surface)
        
        if max_surface:
            queryset = queryset.filter(house__surface__lte=max_surface)
        
        if furnished and furnished != 'Tous':
            queryset = queryset.filter(house__furnished=furnished)

        if garden:
            queryset = queryset.filter(house__garden=True)
        if parking:
            queryset = queryset.filter(house__parking=True)
        if balcony:
            queryset = queryset.filter(house__balcony=True)
        if ac:
            queryset = queryset.filter(house__ac=True)
        if elevator:
            queryset = queryset.filter(house__elevator=True)
        if heating:
            queryset = queryset.filter(house__heating=True)
            
        liked_offer = Like_Offer.objects.filter(user = request.user).values_list('offer',flat=True)
        return render(request,'pages/home/home.html',{"annonces":queryset,"liked_offer":liked_offer,"active":True})
    
    return redirect('homepage')

@login_required(login_url='/app1/login/')
def refuser_annonce(request , id ):
    try : 
        annonce = get_object_or_404(ColocationOffer , id = id )
        annonce.status = "Refusé"
        annonce.save()
        Notification.objects.create(
        destinataire = annonce.owner , 
        message = (
            f"Bonjour, nous vous informons que votre annonce de location portant l'ID : {annonce.id} a été refusée. "
            f"Veuillez vérifier que les informations fournies respectent nos critères de publication. "
            f"Vous pouvez la modifier et la soumettre à nouveau depuis votre espace."
            )
        )
        messages.success(request,f"Annonce {annonce.id} refusée avec succés")
    except Exception as e :
        messages.error(request,f"Une erreur est survenue : {str(e)}")
    return redirect('dashboard_page')

@login_required(login_url='/app1/login/')
def accepter_annonce(request , id ):
    try : 
        annonce = get_object_or_404(ColocationOffer , id = id )
        annonce.status = "Disponible"
        annonce.save()
        Notification.objects.create(
        destinataire = annonce.owner , 
        message = (
            f"Bonjour, votre annonce de location portant l'ID : {annonce.id} a été acceptée. "
            f"Elle est désormais visible par les étudiants sur la plateforme. "
            f"Nous vous remercions pour votre confiance."
            )
        )
        messages.success(request,f"Annonce {annonce.id} accpetée avec succés")
    except Exception as e :
        messages.error(request,f"Une erreur est survenue : {str(e)}")
    return redirect('dashboard_page')

@login_required(login_url='/app1/login/')
def postuler_annonce(request,owner_id,offre_id):
    owner = get_object_or_404(CustomUser , id = owner_id)
    offre = get_object_or_404(ColocationOffer , id = offre_id)
    if not request.user.activation :
        messages.error(request,"Impossible de postuler sans la confirmation de votre compte par un admin merci d'avance")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 
    if  request.user.status != "Étudiant":
        messages.error(request,"Impossible de postuler à une offre car vous avez pas le status Étudiant")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 
    if Candidature.objects.filter(sender = request.user , status = "EN ATTENTE").exists():
        messages.error(request,"Impossible de postuler à une autre offre lorsque vous avez une requête en attente")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 
    if Candidature.objects.filter(owner = owner , sender = request.user , status = "EN ATTENTE").exists():
        messages.error(request,"Impossible de postuler plusieurs fois pour la même offre")
        return redirect('annonce_page',offre.id)
    Candidature.objects.create(
        owner = owner , 
        sender = request.user , 
        offre = offre , 
    )
    Notification.objects.create(
        destinataire = owner , 
        message =  (
            f"Bonjour, vous avez reçu une nouvelle candidature pour votre offre de location d'ID : {offre.id} "
            f"Un candidat ({request.user.email} - {request.user.username}) a soumis son dossier et attend votre retour. "
            f"Nous vous invitons à consulter les détails de cette candidature dans votre espace."
        )
    )
    messages.success(request,f"Votre offre a été enregistrée avec succés")
    return redirect('annonce_page',offre.id)

def accept_profil_locataire(request,cand_id):
    candidature = get_object_or_404(Candidature , id = cand_id)
    offre = get_object_or_404(ColocationOffer , id = candidature.offre.id)
    if offre.nombre_personne >= 1:
        offre.nombre_personne -= 1
        candidature.status = "APPROUVÉE"
        candidature.save()
        messages.success(request,f"La candidature #CAN{candidature.id} a été acceptée avec succés")
        offre.save()
        Notification.objects.create(
        destinataire = candidature.sender , 
        message =  (
            f"Bonjour ta condidature pour l'offre ( ID : {candidature.offre.id} ) a été acceptée"
            f"Merci de contacter l'owner de l'offre afin de finir les démarches administratives merci d'avance"
        )
    )
    else:
        messages.error(request, "Impossible d'accepter davantage de locataires.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def refuse_profil_locataire(request,cand_id):
    candidature = get_object_or_404(Candidature , id = cand_id)
    candidature.status = "REFUSÉE"
    candidature.save()
    Notification.objects.create(
        destinataire = candidature.sender , 
        message =  (
            f"Bonjour ta condidature pour l'offre ( ID : {candidature.offre.id} ) a été refusée suite à plusieurs raisons"
            f"Pour plus de détails merci de contacter l'owner de l'offre"
            f"Merci d'avance."
        )
    )
    messages.error(request,f"La candidature #CAN{candidature.id} a été refusée avec succés")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#les fonctions pour configurer les templates de l'email 
def verify_email(request,Email):
    user = get_object_or_404(CustomUser,email = Email)
    user.Email_Verifiyed = timezone.now().date()
    user.save()
    return redirect('verification_finish')

#les fonctions d'authentifications 
def register_action(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if not request.POST.get('politique'):
                messages.error(request,"Merci d'accepter nos conditions politiques")
                return redirect('register')
            print(form)
            form.save()
            context = {
                'username' : request.POST.get('username') , 
                'email' : request.POST.get('email') 
            }

            html_content = render_to_string('mail/verification.html' ,context)
            optimized_html = transform(html_content)
            email = EmailMultiAlternatives(
                subject='Confirmation d\'email ',
                body=strip_tags(optimized_html),
                from_email='nodej1887@gmail.com',
                to=[request.POST.get('email')],
            )
            email.attach_alternative(optimized_html, "text/html")
            email.send()
            messages.success(request,'Inscription avec succés , veuillez vérifier votre adresse email avant de se connecter')
            return redirect('login')
        else :
            messages.error(request,form.errors)
    else :
        form = CustomUserCreationForm()
    return render(request,'auth/register.html',{"form":form})

def login_page(request):
    return render(request,'auth/login.html')

def login_action(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = get_object_or_404(CustomUser , email = email ).username
        except Http404 :
            messages.error(request,'Adresse email ne correspond à aucun compte')
            return redirect('login')
        user = authenticate(request , username = username , password = password )
        if user is not None :
            if user.Email_Verifiyed is None :
                messages.error(request,"Merci de vérifier votre adresse email")
                return redirect("login")
            login(request,user)
            messages.success(request,'Connexion avec succés')
            return redirect('homepage')
        else :
            messages.error(request,"Email or password incorrect")
            return redirect('login')
    else :
        messages.error(request,'Une erreur est servenue')
        return redirect('login')

def logout_action(request):
    logout(request)
    messages.success(request,"Déconnexion avec succés")
    return redirect('login')

def mdp(request):
    if request.method == "POST" : 
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            relative_url = reverse('change_mdp_page', kwargs={'user_id': user.id})
            reset_url = request.build_absolute_uri(relative_url)
            html_content = render_to_string('mail/mdp.html' ,{"user" : user , "url" : reset_url })
            optimized_html = transform(html_content)
            email = EmailMultiAlternatives(
                subject='Confirmation d\'email ',
                body=strip_tags(optimized_html),
                from_email='nodej1887@gmail.com',
                to=[user.email],
            )
            email.attach_alternative(optimized_html, "text/html")
            email.send()
            messages.success(request,'Un email de restauration de mot de passe a été envoyé avec succés')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except CustomUser.DoesNotExist:
            messages.error(request, "L'email que vous avez fourni ne correspond à aucun utilisateur.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

def change_mdp_page(request,user_id):
    user = get_object_or_404(CustomUser , id = user_id)
    return render(request,"auth/change_mdp.html" , {"user" : user })

def change_mdp_action(request, user_id):
    if request.method == "POST":
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm')

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            user = CustomUser.objects.get(id=user_id)
            if check_password(password1 , user.password):
                messages.error(request,"Veuillez saisir un mot de passe diffrent de celui actuel")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            
            user.password = make_password(password1)
            user.save()

            maroc_tz = pytz.timezone("Africa/Casablanca")
            current_time = datetime.now(maroc_tz)
            formatted_date = current_time.strftime("%d %B %Y, %H:%M (UTC%z)")
            formatted_date = formatted_date.replace("UTC+0100", "UTC+1").replace("UTC+0000", "UTC+0")

            device_info = get_device_info(request)

            html_content = render_to_string(
                'mail/confirmation_mdp.html',
                {
                    "user": user,
                    "modif_date": formatted_date,
                    "device_info": device_info
                }
            )
            optimized_html = transform(html_content)
            email = EmailMultiAlternatives(
                subject='Confirmation du changement de mot de passe',
                body=strip_tags(optimized_html),
                from_email='nodej1887@gmail.com',
                to=[user.email],
            )
            email.attach_alternative(optimized_html, "text/html")
            email.send()

            messages.success(request, "Mot de passe modifié avec succès !")
            return redirect('login')

        except CustomUser.DoesNotExist:
            messages.error(request, "Une erreur est survenue.")
            return redirect('login')
        
#Template en relation avec le profile de l'utilisateur 
@login_required(login_url='/app1/login/')
def profile_page(request , username):
    return render(request,"private/profile.html")

@login_required
def change_password_profile(request , username):
    if request.method == "POST" : 
        old_password = request.POST.get('password')
        new_password = request.POST.get('password_new')
        user = get_object_or_404(CustomUser,username = username)
        if check_password(old_password , user.password):
            if check_password(new_password , user.password):
                messages.error(request,"Veuillez saisir un nouveau mot de passe différent de celui actuel ")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            try :
                user.password = make_password(new_password)
                user.save()
                context = {
                    'username' : user.username , 
                }
                html_content = render_to_string('mail/modification_password.html' ,context)
                optimized_html = transform(html_content)
                email = EmailMultiAlternatives(
                    subject='Alerte modification de password',
                    body=strip_tags(optimized_html),
                    from_email='nodej1887@gmail.com',
                    to=[user.email],
                )
                email.attach_alternative(optimized_html, "text/html")
                email.send()
                messages.success(request,"Modification de password avec succés")
                return redirect('login')
            except Exception as e : 
                messages.error(request,"Erreur : " , e )
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else :
            messages.error(request,'Vous avez pas saisi le bon mot de passe')
            return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/app1/login/')
def delete_profile(request,username):
    user = get_object_or_404(CustomUser , username = username)
    if not user.activation :
        messages.error(request,"Vous pouvez pas supprimé votre compte avant d\'être vérifier par un admin")
        return redirect("profilepage",username) 
    user.delete()
    messages.success(request,"Suppression avec succés")
    return redirect('login')

@login_required(login_url='/app1/login/')
def edit_profile(request,username):
    user = request.user
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if user.status == "Étudiant":
                etudiant = Etudiant.objects.get(user = user)
                etudiant.universite = request.POST.get('universite')
                etudiant.niveau_scolaire = request.POST.get('niveau_scolaire')
                if request.POST.get('bourse') == "Boursier" : 
                    etudiant.bourse = True 
                    etudiant.montant_bourse = request.POST.get('montant_bourse')
                else :
                    etudiant.bourse = False
                    etudiant.montant_bourse = 0.00
                if request.POST.get('job_etudiant') == "Employé" :
                    etudiant.job_etudiant = True
                    etudiant.job_etudiant_name = request.POST.get('job_etudiant_name')
                    etudiant.job_etudiant_revenu = request.POST.get('job_etudiant_revenu')
                else : 
                    etudiant.job_etudiant = False
                    etudiant.job_etudiant_name = ""
                    etudiant.job_etudiant_revenu = 0.00
                etudiant.save()
            form.save()
            messages.success(request,'Modification de vos données avec succés')
            return redirect('profilepage',request.user.username)  
    else:
        form = CustomUserUpdateForm(instance=user)
    return render(request, 'private/edit_profile.html', {'form': form})

def dashboard_profile(request):
    users = CustomUser.objects.all()
    offres = ColocationOffer.objects.all()
    users_count = CustomUser.objects.exclude(status = "Admin").count()
    offres_count = ColocationOffer.objects.all().count()
    offres_attente = ColocationOffer.objects.filter(status = "En attente").count()
    houses_count = House.objects.all().count()
    return render(request,'private/dashboard.html',{"users" : users , "offres" : offres , "user_count" : users_count , "offer_count" : offres_count , "order_attente" : offres_attente , "house_count" : houses_count})

@login_required(login_url='/app1/login/')
def favorite_page(request):
    liked_offer = Like_Offer.objects.filter(user = request.user)
    return render(request,"private/favoris.html",{"offer":liked_offer})

@login_required(login_url='/app1/login/')
def messages_page(request):
    other_users = []
    chats = Thread.objects.all().order_by('-last_updated')
    for x in chats :
        if x.user1 == request.user or x.user2 == request.user:
            other_users.append(x.get_other_user(request.user))
    count = len(other_users)
    return render(request,"private/messages.html",{"other" : other_users , "count" : count})
        
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        try:
            content = request.POST.get("content")
            thread_id = request.POST.get("thread_id")

            if not content or not thread_id:
                return JsonResponse({"error": "Champ vide"}, status=400)

            thread = Thread.objects.get(id=thread_id)
            message = Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )

            thread.last_updated = timezone.now()
            thread.save()

            return JsonResponse({
                "content": message.content,
                "sender": "Vous",
                "timestamp": message.timestamp.strftime("%H:%M")
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@login_required(login_url='/app1/login/')
def specific_chat(request,destinataire):
    other_user = get_object_or_404(CustomUser , id = destinataire)
    chat = Thread.objects.filter(Q(user1=other_user, user2=request.user) | Q(user1=request.user, user2=other_user)).first()
    if not chat :
        Thread.objects.create(
            user1 = request.user ,
            user2 = other_user ,
        )
    messages = Message.objects.filter(thread=chat)  
    for message in messages :
        message.is_read = True 
        message.save()
    other_users = []
    chats = Thread.objects.all().order_by('-last_updated')
    count = chats.count()
    for x in chats :
        if x.user1 == request.user or x.user2 == request.user:
            other_users.append(x.get_other_user(request.user)) 
    count = len(other_users)
    return render(request,'private/specific_chat.html',{"messages" : messages , "other" : other_users , "destinataire" : other_user , "thread" : chat ,  "count" : count })

@login_required(login_url='/app1/login/')
def  boite_reception(request):
    offres = Candidature.objects.filter(owner=request.user).order_by('-created_at')
    total = Candidature.objects.filter(owner = request.user).count()
    attente = Candidature.objects.filter(owner = request.user , status = "EN ATTENTE").count()
    return render(request,'private/recevoir.html',{"offres" : offres , "total" : total , "attente" : attente})

@login_required(login_url='/app1/login/')
def other_profile(request,user_id):
    user = CustomUser.objects.get(id = user_id)
    return render(request,'private/other_profile.html',{"user" : user})

@login_required(login_url='/app1/login/')
def supprimer_user (request,user_id):
    try : 
        user = get_object_or_404(CustomUser , id = user_id)
        user.delete()
        messages.success(request,f"Utilisateur f{user.username} a été supprimé avec succés")
    except Exception as e : 
        messages.error(request , "Une erreur est servenue " , e )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def activation_user(request,user_id):
    try : 
        utilisateur = get_object_or_404(CustomUser , id = user_id)
        utilisateur.activation = True 
        utilisateur.save()
        messages.success(request,f"Le compte de l'utilisateur {utilisateur.username} a été activé avec succés!")
    except Exception as e : 
        messages.error(request,"Une erreur est survenue : " , e )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/app1/login/')
def vos_candidatures(request):
    cand = Candidature.objects.filter(sender = request.user).order_by("-created_at")
    pending_count = Candidature.objects.filter(sender=request.user , status = "EN ATTENTE").count()
    refuse_count = Candidature.objects.filter(sender = request.user , status = "REFUSÉE").count()
    accept_count = Candidature.objects.filter(sender = request.user , status = "APPROUVÉE").count()
    return render(request,'private/vos_candidatures.html',{"candidatures" : cand , "pending" : pending_count , "refuse" : refuse_count , "accept" : accept_count})

def vos_candidatures_filter(request):
    pending_count = Candidature.objects.filter(sender=request.user , status = "EN ATTENTE").count()
    refuse_count = Candidature.objects.filter(sender = request.user , status = "REFUSÉE").count()
    accept_count = Candidature.objects.filter(sender = request.user , status = "APPROUVÉE").count()
    if request.method == "POST" :
        status = request.POST.get('status')
        if status == "default":
            cand = Candidature.objects.filter(sender = request.user).order_by("-created_at")
        else :
            cand = Candidature.objects.filter(sender = request.user , status = status ).order_by("-created_at")
    else :
        cand = Candidature.objects.filter(sender = request.user).order_by("-created_at")
    return render(request,'private/vos_candidatures.html',{"candidatures" : cand , "pending" : pending_count , "refuse" : refuse_count , "accept" : accept_count})

@login_required(login_url='/app1/login/')
def notification_page(request):
    notifs = Notification.objects.filter(destinataire = request.user).order_by("-created_at")
    for notif in notifs :
        notif.is_read = True 
        notif.save()
    return render(request,"private/notification.html",{"notifs" : notifs})

#Fonction en relation avec le FaceID 
def register_face(request, username):
    cap = cv2.VideoCapture(0)  

    if not cap.isOpened():
        messages.error(request,'Impossible d\'accéder à la caméra')
        return redirect('profilepage',username)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    time.sleep(2)

    ret, frame = cap.read()
    cap.release()  

    if not ret:
        messages.error(request,'Échec de la capture d\'image')
        return redirect('profilepage',username)

    folder_path = os.path.join(settings.MEDIA_ROOT, "profileimage")
    os.makedirs(folder_path, exist_ok=True)  

    image_name = f"{username}.jpg"
    image_path = os.path.join(folder_path, image_name)

    cv2.imwrite(image_path, frame)  

    user, created = CustomUser.objects.get_or_create(username=username)
    user.ProfileImage = f"profileimage/{image_name}"
    user.save()
    
    messages.success(request,'Image enregistrée')
    return redirect('profilepage',username)

#Fonction en relation avec l'option add to favorite
@login_required(login_url='/app1/login/')
def favorite(request,id,username):
    poste = get_object_or_404(ColocationOffer , id = id )
    utilisateur = get_object_or_404(CustomUser , username = username)
    like = Like_Offer.objects.filter(offer=poste, user=utilisateur)
    if like.exists() :
        like.delete()
        return redirect('homepage')
    else :
        Like_Offer.objects.create(offer=poste, user=utilisateur)
    return redirect('favoritepage')

#Aide
def centre_aide_page(request):
    return render(request,"pages/centre_aide.html")

def contact_page(request):
    return render(request,"pages/contact.html")

def contact_action(request):
    if request.method == "POST" :
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        context = {
            "name" : name , 
            "email" : email , 
            "phone" : phone , 
            "subject" : subject , 
            "message" : message ,
            "today" : date.today()
         }
        html_content = render_to_string('mail/reclamation.html' ,context)
        optimized_html = transform(html_content)
        email = EmailMultiAlternatives(
            subject='Confirmation d\'email ',
            body=strip_tags(optimized_html),
            from_email='nodej1887@gmail.com',
            to=["a.lahbichi2004@gmail.com"],
        )
        email.attach_alternative(optimized_html, "text/html")
        email.send()
        messages.success(request,"L'email a été envoyé avec succés!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
