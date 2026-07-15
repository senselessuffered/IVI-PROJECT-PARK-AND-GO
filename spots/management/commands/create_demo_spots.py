from django.core.management.base import BaseCommand

from spots.models import ParkingSpot


class Command(BaseCommand):
    help = 'Создаёт демо-парковочные места (P-001, P-002, ...).'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50)

    def handle(self, *args, **options):
        count = options['count']
        created = 0
        for number in range(1, count + 1):
            _, is_new = ParkingSpot.objects.get_or_create(
                number=f'P-{number:03d}',
                defaults={
                    'description': 'Демо-место для тестового показа',
                    'is_active': True,
                },
            )
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Создано мест: {created} (запрошено {count}).'))
