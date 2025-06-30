from django.contrib import admin # type: ignore
from .models import CustomUser , Etudiant , Candidature ,  ColocationOffer , ColocationPhoto , Like_Offer , City , House , Thread , Message , Entrepreneur , Réglamation , Notification


admin.site.register(CustomUser)
admin.site.register(ColocationOffer)
admin.site.register(ColocationPhoto)
admin.site.register(Like_Offer)
admin.site.register(City)
admin.site.register(House)
admin.site.register(Thread)
admin.site.register(Message)
admin.site.register(Etudiant)
admin.site.register(Réglamation)
admin.site.register(Candidature)
admin.site.register(Entrepreneur)
admin.site.register(Notification)
