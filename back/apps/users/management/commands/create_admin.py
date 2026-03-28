from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create an admin user if one does not already exist."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Admin email address")
        parser.add_argument("--password", required=True, help="Admin password")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        if User.objects.filter(email=email).exists():
            self.stdout.write("Admin already exists")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
        )
        self.stdout.write(f"Admin user created: {email}")
