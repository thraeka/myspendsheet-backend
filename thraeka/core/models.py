from django.contrib.auth.models import User
from django.db import models


class Txn(models.Model):
    """
    Model representing transaction (txn)

    This model stores info on individual txn: date, description, amount, category, source,
    and the date of input.

    Attributes:
        date (DateField): date of txn
        description (CharField): short description of txn
        amount (DecimalField): txn amount in $
        category (CharField): category of txn
        source (CharField): source of txn (i.e bank, cash)
        source_name (CharField): name of source
        date_of_input (DateField): date the txn was recorded

    TODO:
        - create model for categories per user with default instances
        - create model for tags per user
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="txns")
    date = models.DateField()
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    category = models.CharField(max_length=100)
    # Using SQLite for inital testing. Adding tags once migrate db to Postgres
    # tags = models.ArrayField()
    source = models.CharField(max_length=100)
    source_name = models.CharField(max_length=100)
    date_of_input = models.DateField()
