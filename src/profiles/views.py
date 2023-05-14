from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import EditPersonalData, EditProfileImage
from .models import Profile
from .tasks import background_store_img_form


def public_profile(req: HttpRequest, username: str) -> TemplateResponse:
    return TemplateResponse(
        req,
        "profiles/detail.html",
        {"profile": get_object_or_404(Profile, user__username=username)},
    )


@login_required
def tab_personal_data(req: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        req,
        "profiles/tab_personal.html",
        {"form": EditPersonalData(instance=req.user.profile)},  # type: ignore
    )


@login_required
def tab_account_data(req: HttpRequest) -> TemplateResponse:
    return TemplateResponse(
        req, "profiles/tab_account.html", {"img_form": EditProfileImage}
    )


@login_required
@require_POST
def hx_personal_data_post(req: HttpRequest) -> TemplateResponse:
    form = EditPersonalData(data=req.POST, instance=req.user.profile)  # type: ignore
    if form.is_valid():
        form.save()
        messages.add_message(req, messages.SUCCESS, "General fields updated!")
    return TemplateResponse(req, "profiles/tab_personal.html", {"form": form})


@login_required
@require_POST
def hx_img_post(req: HttpRequest) -> HttpResponseRedirect:
    if upload := req.FILES.get("id_image"):
        form = EditProfileImage(req.POST, req.FILES, instance=req.user.profile)  # type: ignore # noqa: E501
        if form.is_valid():
            background_store_img_form(upload, form.instance.image, form.instance.im_key)
            messages.add_message(
                req,
                messages.SUCCESS,
                "Image being processed! Should be available soon.",
            )
        else:
            if err_msg := form.errors.get("image"):
                for msg in err_msg:
                    messages.add_message(req, messages.ERROR, msg)
    return HttpResponseRedirect(reverse("profiles:settings_account_data"))


@login_required
@require_POST
def hx_del_user_post(req: HttpRequest) -> HttpResponseRedirect:
    if req.user.is_active:
        req.user.delete()  # TODO: how to show message on redirect
    return HttpResponseRedirect(reverse("pages:home"))
