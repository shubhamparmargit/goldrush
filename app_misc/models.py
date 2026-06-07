from django.db import models

class AppVersion(models.Model):
    class Meta:
        db_table = 'app_version'
    version_number = models.CharField(max_length=10, null=True, blank=True)