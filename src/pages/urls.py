from django.urls import path
from django.urls.resolvers import URLPattern

from .views import ContactFormView, HomePage, LegalPage, PopularPage

app_name = "pages"
urlpatterns: list[URLPattern] = [
    path("legal/<slug:category>", LegalPage.as_view(), name="legal"),
    path("contact", ContactFormView.as_view(), name="contact"),
    path("popular", PopularPage.as_view(), name="popular"),
    path("", HomePage.as_view(), name="home"),
]
