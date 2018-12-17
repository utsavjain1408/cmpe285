from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    # This will contain a json array of tickers
    stocks_selected = models.TextField(max_length=500, blank=True)
    stock_number = models.TextField(max_length=500, blank=True)
    amount_invested = models.FloatField(default=0)
    residual_amount = models.FloatField(default=0)