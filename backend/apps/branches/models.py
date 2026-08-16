from django.db import models

from apps.core.models import BaseModel


class Branch(BaseModel):
    """A restaurant branch/location. Demo UAE locations only — not real branches."""

    name = models.CharField(max_length=150, db_index=True)
    code = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.code})"
