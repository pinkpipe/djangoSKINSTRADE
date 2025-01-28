from django.db import models


class UserST(models.Model):
    username = models.CharField(max_length=25)
    registered_date = models.DateTimeField(auto_now_add=True)
    trade_link = models.URLField(default='', blank=True)
    count_buy = models.PositiveIntegerField(default=0)
    count_sell = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    inventory_json = models.JSONField(default=dict, blank=True)
    steam_ID = models.CharField(max_length=17, unique=True)
    email = models.EmailField(null=True, unique=True)
    telegram = models.CharField(max_length=20, null=True, unique=True)

    def __str__(self):
        return self.steam_ID


class ItemST(models.Model):
    item_steam_ID = models.CharField(max_length=25, null=True, unique=True)
    user = models.ForeignKey(UserST, on_delete=models.CASCADE, related_name='items', null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    status_trade = models.BooleanField(default=True)
    date_push_item = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_steam_ID


class TradeST(models.Model):
    STATUS_CHOICES = (
        ('получен', 'Получен'),
        ('ожидает оплаты', 'Ожидает оплаты'),
        ('отменен', 'Отменен')
    )

    trade_status_st = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ожидает оплаты')
    item = models.ForeignKey(ItemST, on_delete=models.CASCADE, related_name='trades')
    buyer_ID = models.CharField(max_length=17, null=True)
    date_push_trade = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade {self.item.user.steam_ID}: {self.item.item_steam_ID} -> {self.buyer_ID}"
