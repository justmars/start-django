from pathlib import Path

import yaml
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class AgreementRecentManager(models.Manager):
    def ensure_terms(self):
        if agreement := self.model.objects.first():
            return agreement

        file = Path(__file__).parent / "fixtures" / "legal.yml"
        if not file.exists():
            raise Exception(f"Missing {file}.")
        for legal in yaml.safe_load(file.read_bytes()):
            self.model.objects.create(**legal["fields"])
        return agreement

    def get_latest(self, category: str):
        cat = self.model.Category[category.upper()]  # matches Enum
        return super().get_queryset().filter(category=cat).latest()

    def updated_ver(self, category: str):
        try:
            return self.get_latest(category)
        except ObjectDoesNotExist:
            self.ensure_terms()
            return self.get_latest(category)
