from django.core.management.base import BaseCommand, CommandError

from usuarios.models import Cliente


class Command(BaseCommand):
    help = 'Crea un cliente activo'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)

    def handle(self, *args, **options):
        Cliente.objects.create_user(options['email'][0], options['password'][0])
