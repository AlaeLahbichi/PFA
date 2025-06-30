from django.urls import path  # type: ignore
from .views import * 

urlpatterns = [

    #URL => pour afficher les tamplates pricipaux
    path('verification_finish/',verification_finish,name="verification_finish"),
    path('home/',Home_Page,name="homepage"),
    path('home_off/',Home_Page_Off,name="homepage_off"),
    path('add_annonce/',ajouter_annonce_colocation,name="add_annonce_location"),
    path('add_house/',ajouter_house_action,name="ajouter_house_action"),
    path('annonce/<int:code>',annonce_page,name="annonce_page"),
    path('annonce-refused/<int:id>',refuser_annonce,name="annoncerefuser"),
    path('annonce-accepted/<int:id>',accepter_annonce,name="annonceaccepter"),
    path('postuler-offre/<int:owner_id>/<int:offre_id>',postuler_annonce,name="postuler_annonce"),
    path('supprimer_annonce_admin/<int:id>/',supprimer_annonce_admin,name="supprimer_annonce_admin"),
    path('mes_annonces/',mes_annonces_page,name="mes_annonces"),
    path('modifier_annonce/<int:id>',modifier_annonce,name="modifier_annonce"),
    path('modifier_annonce_action/<int:id>',modifier_annonce_action,name="modifier_annonce_action"),
    path('supprimer_annonce/<int:id>',supprimer_annonce,name="supprimer_annonce"),

    #URL=> pour configurer les templates de l'email 
    path('Validate_Email/<str:Email>',verify_email,name="Validate_Email"),

    #URL => Authentification
    path('login/',login_page,name="login"),
    path('login-action/',login_action,name="login-action"),
    path('register/',register_action,name="register"),
    path('logout-action/',logout_action,name="logout"),
    path('change_mdp_page/<int:user_id>',change_mdp_page,name="change_mdp_page"),
    path('change_mdp_action/<int:user_id>',change_mdp_action,name="change_mdp_action"),
    path('mdp_request/',mdp,name="mdp_request"),

    #URL => Profile
    path('profilepage/<str:username>/',profile_page,name="profilepage"),
    path('change_password/<str:username>/',change_password_profile,name="changepassword"),
    path('edit_profile/<str:username>/',edit_profile,name="editprofile"),
    path('dashboard-page/',dashboard_profile,name="dashboard_page"),
    path('favorite_page/',favorite_page,name="favoritepage"),
    path('messages_page/',messages_page,name="messagepages"),
    path('specific_chat/<int:destinataire>',specific_chat,name="specificmessages"),
    path('send-message/', send_message, name='send_message'),
    path('reception/', boite_reception, name='boite_reception_page'),
    path('other_profile/<int:user_id>',other_profile,name="other_profile"),
    path('activate_user/<int:user_id>',activation_user,name="activate_user"),
    path('vos_candidatures/',vos_candidatures,name="vos_candidatures"),
    path('vos_candidature_filter/',vos_candidatures_filter,name="vos_candidature_filter"),
    path('notification_page/',notification_page,name="notification_page"),

    #URL => FaceID 
    path('prendrephoto/<str:username>/',register_face,name="prendrephoto"),

    #URL => Like a post 
    path('add-remove-offer/<int:id>/<str:username>',favorite,name="favoriteoffer"),

    #URL => url en lien avec les annonces 
    path('filter-annonce/',filter_colocation,name="filterannonce"),
    path('accept-candidature/<int:cand_id>',accept_profil_locataire,name="accept_cand"),
    path('refuse-candidature/<int:cand_id>',refuse_profil_locataire,name="refuse_cand"),

    #Aide 
    path('centre_aide/',centre_aide_page,name="centre_aide"),
    path('contact_page/',contact_page,name="contact_page"),
    path('supprimer_user/<int:user_id>',supprimer_user,name="supprimer_user"),
    path('contact_action/',contact_action,name="contact_action"),

]
