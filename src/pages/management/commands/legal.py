from django.core.management.base import BaseCommand

from pages.models import Agreement


class Command(BaseCommand):
    help = "Set legal agreements based on fixtures."

    def handle(self, *args, **options):
        Agreement.bind.ensure_terms()  # auto-create, if not existing
