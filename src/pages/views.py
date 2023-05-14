import json
from pathlib import Path

import yaml
from dateutil.parser import parse
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactForm
from .models import Agreement


class HomePage(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homefile = Path(__file__).parent / "fixtures" / "home.yml"
        homedata = yaml.safe_load(homefile.read_bytes())
        features = homedata["home"]["features"]
        for feature in features:
            if links := feature.get("links"):
                for link in links:
                    link |= {"icon_name": link.get("icon_name", "shield_check")}
        context["features"] = features
        return context


class PopularPage(TemplateView):
    template_name = "pages/popular.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sitesfile = Path(__file__).parent / "fixtures" / "x.yml"
        sitesdata = yaml.safe_load(sitesfile.read_bytes())
        for site in sitesdata:
            site |= {
                "updated_at": parse(site["updated_at"]),
                "created_at": parse(site["created_at"]),
                "timestamp": parse(site["timestamp"]),
                "github_url": (
                    f"https://github.com/{site['owner_name']}/{site['repo_name']}"
                ),
                "topics_list": json.loads(site["topics_list"]),
            }
        sitesdata.sort(key=lambda item: item["created_at"])
        context["starters"] = sitesdata
        return context


class LegalPage(TemplateView):
    template_name = "pages/legal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if category := kwargs.get("category"):
            context["agreement"] = Agreement.bind.updated_ver(category=category)
            context["clauses"] = [{"hello": "world"} for i in range(10)]
        return context


class ContactFormView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["form_title"] = f"Say Hi, {self.request.user}!"
        return context

    def get_initial(self):
        """If user already logged in, has email address, populate field."""
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            if self.request.user.email:  # type: ignore
                initial["email"] = self.request.user.email  # type: ignore
        return initial

    def form_invalid(self, form: ContactForm):
        return TemplateResponse(
            self.request, "pages/_contact_form.html", {"form": form}
        )

    def form_valid(self, form: ContactForm):
        if form.is_valid():
            form.send_email(form)
        return TemplateResponse(self.request, "pages/_contact_success.html", {})
