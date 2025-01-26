import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social_django.models import UserSocialAuth

from .steam_api import get_steam_inventory, parse_inventory_items

logger = logging.getLogger(__name__)


def login(request):
    return render(request, "index.html")


@login_required
def home(request):
    try:
        steam_user = UserSocialAuth.objects.get(user=request.user, provider="steam")
        steam_id = steam_user.uid
        player_info = steam_user.extra_data["player"]

        logger.info(f"Getting inventory for Steam ID: {steam_id}")

        # Получаем инвентарь
        inventory_data = get_steam_inventory(steam_id)
        if inventory_data is None:
            logger.error("Failed to get inventory data")
            return render(
                request,
                "successfully.html",
                {
                    "steam_id": steam_id,
                    "player_info": player_info,
                    "error": "Failed to load inventory",
                },
            )

        inventory_items = parse_inventory_items(inventory_data)
        logger.info(f"Retrieved {len(inventory_items)} inventory items")

        context = {
            "steam_id": steam_id,
            "player_info": player_info,
            "inventory_items": inventory_items,
        }
        return render(request, "successfully.html", context)
    except UserSocialAuth.DoesNotExist:
        logger.error("Steam authentication not found")
        return render(
            request, "successfully.html", {"error": "Steam authentication not found"}
        )
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        return render(request, "successfully.html", {"error": str(e)})
