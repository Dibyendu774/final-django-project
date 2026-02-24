from .views import *
from django.urls import path, include

urlpatterns = [
    path('', Home),
    path('Register-Page', Register),
    path('Login-Page', Login),
    path('Logout', Logout),
    path('DashBoard', DashBoard),
    path('DashTable', DataTable),
    path('Edit/<int:id>', Edit),
    path('Delete/<int:user_id>', Delete),
    path('Forget/<int:id>', Forget),
    path('Otp/<int:id>', Otp),
    path('Google_T', Google_T),
    path('Order', Order),
    path('Add-Product', Add_Product),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('Display', Display),
    path('add-cart', Cart)
]