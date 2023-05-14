from django.urls import path
from django.urls.resolvers import URLPattern

from .views import (
    hx_del_user_post,
    hx_img_post,
    hx_personal_data_post,
    public_profile,
    tab_account_data,
    tab_personal_data,
)

app_name = "profiles"
urlpatterns: list[URLPattern] = [
    path(
        route="u/<slug:username>",
        view=public_profile,
        name="detail",
    ),
    path(
        route="settings/personal_data/post",
        view=hx_personal_data_post,
        name="hx_personal_data_post",
    ),
    path(
        route="settings/image/post",
        view=hx_img_post,
        name="hx_img_post",
    ),
    path(
        route="settings/security/user/delete/post",
        view=hx_del_user_post,
        name="hx_del_user_post",
    ),
    path(
        route="settings/account_data",
        view=tab_account_data,
        name="settings_account_data",
    ),
    path(
        route="",
        view=tab_personal_data,
        name="settings",
    ),
]
