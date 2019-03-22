# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class AccountMoney(models.Model):
    id_account = models.IntegerField(primary_key=True)
    balance = models.CharField(max_length=45, blank=True, null=True)
    last_transaction = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_money'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Transactions(models.Model):
    id_transactions = models.IntegerField(primary_key=True)
    id_sender = models.CharField(max_length=45, blank=True, null=True)
    id_receiver = models.CharField(max_length=45, blank=True, null=True)
    amount = models.CharField(max_length=45, blank=True, null=True)
    datetime = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions'


class Users(models.Model):
    id_users = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=60, blank=True, null=True)
    location = models.CharField(max_length=45, blank=True, null=True)
    #balance = models.DecimalField(max_digits=60, decimal_places=2, blank=True, null=True)
    email = models.CharField(max_length=120, blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    cookies = models.CharField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        # return str(self.facility_id + self.facility_name + self.total_occupancy + self.current_occupancy)
        return "id_users: " + str(self.id_users) + ', username: ' + str(self.username) + ', password: ' + str(self.password)
    
    class Meta:
        managed = False
        db_table = 'users'

        
# class FacOverview(models.Model):
#     date = models.DateField(primary_key=True)
#     facility_id = models.IntegerField(primary_key=True)
#     total_occupancy = models.CharField(max_length=45, blank=True, null=True)
#     current_occupancy = models.CharField(max_length=45, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'fac_overview'
#         unique_together = (('date', 'facility_id'),)

class FacOverview(models.Model):
    date = models.DateField(primary_key=True)
    time = models.CharField(primary_key=True, max_length=45)
    facility_id = models.IntegerField(primary_key=True)
    total_occupancy = models.CharField(max_length=45, blank=True, null=True)
    current_occupancy = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fac_overview'
        unique_together = (('date', 'time', 'facility_id'),)

class Facilities(models.Model):
    facility_id = models.IntegerField(primary_key=True)
    facility_name = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facilities'