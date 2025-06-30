from django.db.models.signals import post_save , pre_save # type: ignore
from django.dispatch import receiver # type: ignore
from .models import CustomUser , Etudiant , ColocationOffer
from decimal import Decimal


@receiver(post_save, sender=CustomUser)
def create_related_profile(sender, instance, created, **kwargs):
    if created:  
        if instance.status == 'Étudiant':
            Etudiant.objects.create(user=instance)

@receiver(pre_save, sender=Etudiant)
def update_revenu_total(sender, instance, **kwargs):
    revenu = Decimal('0.00')

    if instance.bourse:
        try:
            revenu += Decimal(instance.montant_bourse or '0')
        except:
            revenu += Decimal('0')

    if instance.job_etudiant:
        try:
            revenu += Decimal(instance.job_etudiant_revenu or '0')
        except:
            revenu += Decimal('0')

    instance.revenu_mensuel_total = revenu

@receiver(pre_save, sender=ColocationOffer)
def modifier_status_offre(sender, instance, **kwargs):
    if instance.nombre_personne == 0 :
        instance.status = "Fini"