
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name='home'),
    path("new", views.regevent, name='regevent'),
    path("update_loc", views.update_loc, name="update_loc"),
    path("register", views.register, name="register"),
    path("login", views.sign_in, name="login"),
    path("logout", views.signout, name="logout"),
    path("ev_details/<int:id>", views.ev_details, name="ev_details"), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

