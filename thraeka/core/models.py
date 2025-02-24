from django.db import models

class Txn(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    category = models.CharField(max_length=100)
    # Using SQLite for inital testing. Adding tags once migrate db to Postgres
    # tags = models.ArrayField()
    source = models.CharField(max_length=100)
    source_name = models.CharField(max_length=100)
    date_of_input = models.DateField()