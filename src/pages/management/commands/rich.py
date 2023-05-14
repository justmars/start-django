from typing import Iterable

from django.conf import settings
from django.core.management.base import BaseCommand
from profiles.utils import select_storage
from rich.console import Console
from rich.table import Table


class Command(BaseCommand):
    help = "Show settings."

    def handle(self, *args, **options):
        def unpack(value: str) -> Iterable:
            """Expects an f-string `value` evaluated with `=`. This will enable
            the splitting of the value into 2 parts; use the first part as
            the setting name and the second part as the setting value."""
            if "=" not in value:
                raise Exception(f"Cannot unpack {value=}")
            parts: list[str] = value.split("=", maxsplit=1)
            parts[0] = parts[0].removeprefix("settings.").lower()
            parts[1] = parts[1].strip("'")
            return parts

        db_engine = settings.DATABASES["default"]["ENGINE"]
        img_storage = select_storage().__class__.__name__
        huey = settings.HUEY.get("huey_class", settings.HUEY.get("connection"))
        tbl = Table(title="Runtime Settings", show_header=False)
        tbl.add_column("Setting", style="purple4")
        tbl.add_column("Value", style="green4", no_wrap=True)
        tbl.add_row(*unpack(f"{settings.DEBUG=}"))
        tbl.add_row(*unpack(f"{db_engine=}"))
        tbl.add_row(*unpack(f"{huey=}"))
        tbl.add_row(*unpack(f"{settings.STATIC_ROOT=}"))
        tbl.add_row(*unpack(f"{settings.COMPRESS_ROOT=}"))
        tbl.add_row(*unpack(f"{settings.EMAIL_BACKEND=}"))
        tbl.add_row(*unpack(f"{img_storage=}"))
        Console().print(tbl)
