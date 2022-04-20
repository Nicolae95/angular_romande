# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
    ADMIN = 1
    VENDEUR = 2
    CLIENT = 3
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (VENDEUR, 'Vendeur'),
        (CLIENT, 'Client'),
    )
    SEX_CHOICES = (
        ('F', 'Madame'),
        ('M', 'Monsieur'),
    )
    FUNC_CHOICES = (
        (1, 'Account Manager'),
        (2, 'Responsable Marchés'),
        (3, 'Directeur'),
        (4, 'CEO'),
        (5, 'Custom'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=2, null=True, blank=True)
    token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    temp = models.UUIDField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    signature = models.FileField(upload_to='signatures/', null=True, blank=True)
    fonction = models.PositiveSmallIntegerField(choices=FUNC_CHOICES, default=2, null=True, blank=True)
    log = models.DateTimeField(null=True, blank=True)
    crm_id = models.IntegerField(null=True, blank=True)
    per_pag = models.IntegerField(default=10, null=True, blank=True)
    other_fonction = models.CharField(max_length=255, null=True, blank=True)
    auth = models.PositiveSmallIntegerField(default=3, null=True, blank=True)
    last_auth = models.DateTimeField(default=datetime.now, null=True, blank=True)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    @property
    def user_function(self):
        """Returns the display value given the db value"""
        for (db_val, display_val) in self.FUNC_CHOICES:
            if db_val == self.fonction and self.fonction != 10:
                return display_val
            if db_val == self.fonction and self.fonction == 10:
                return self.other_fonction
        return ''

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
