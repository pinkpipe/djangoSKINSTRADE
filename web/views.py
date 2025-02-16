import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from social_django.models import UserSocialAuth

from web.models import *

from .steam_api import get_steam_inventory, parse_inventory_items

logger = logging.getLogger(__name__)


def login(request):
    return render(request, "front/index.html")


@login_required
def home(request):
    try:
        steam_user = UserSocialAuth.objects.get(user=request.user, provider="steam")
        steam_id = steam_user.uid
        player_info = steam_user.extra_data.get("player", {})

        # Всегда сначала создаём/получаем пользователя
        user_st, created = UserST.objects.get_or_create(
            steam_ID=steam_id,
            defaults={
                "username": player_info.get("personaname", steam_id),
            },
        )
        if created:
            logger.info(f"Created user {user_st.username}")

        # Далее пробуем получить инвентарь
        inventory_data = get_steam_inventory(steam_id)
        if inventory_data is None:
            logger.error("Failed to get inventory data — probably private or error")
            inventory_items = []
            error_message = "Failed to load inventory (maybe private?)."
        else:
            # Парсим инвентарь
            inventory_items = parse_inventory_items(inventory_data)
            error_message = None

        context = {
            "steam_id": steam_id,
            "player_info": player_info,
            "inventory_items": inventory_items,
            "user_st": user_st,
            "error": error_message,
        }
        return render(request, "front/new_profille.html", context)

    except UserSocialAuth.DoesNotExist:
        logger.error("Steam authentication not found")
        return render(
            request, "successfully.html", {"error": "Steam authentication not found"}
        )
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        return render(request, "successfully.html", {"error": str(e)})


def save_tradelink(request):
    if request.method == "POST":
        tradelink = request.POST.get("tradelink")
        steam_user = UserSocialAuth.objects.get(user=request.user, provider="steam")
        steam_id = steam_user.uid

        if tradelink:
            user = UserST.objects.get(steam_ID=steam_id)
            user.trade_link = tradelink
            user.save()

        return redirect(reverse("home"))
    else:
        return HttpResponse("Недопустимый метод запроса!")


def save_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        steam_user = UserSocialAuth.objects.get(user=request.user, provider="steam")
        steam_id = steam_user.uid

        if email:
            user = UserST.objects.get(steam_ID=steam_id)
            user.email = email
            user.save()

        return redirect(reverse("home"))
    else:
        return HttpResponse("Недопустимый метод запроса!")


def save_telegram(request):
    if request.method == "POST":
        telegram = request.POST.get("telegram")
        steam_user = UserSocialAuth.objects.get(user=request.user, provider="steam")
        steam_id = steam_user.uid

        if telegram:
            user = UserST.objects.get(steam_ID=steam_id)
            user.telegram = telegram
            user.save()

        return redirect(reverse("home"))
    else:
        return HttpResponse("Недопустимый метод запроса!")
