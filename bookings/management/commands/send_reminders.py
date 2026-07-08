from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Рассылка напоминаний по броням'

    def handle(self, *args, **options):
        # TODO PIXELS-019
        pass
