# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Reddit(models.Model):
    index = models.IntegerField(blank=True, null=True)
    id = models.TextField(primary_key=True)
    ups = models.IntegerField(blank=True, null=True)
    subreddit = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    downs = models.IntegerField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reddit'
