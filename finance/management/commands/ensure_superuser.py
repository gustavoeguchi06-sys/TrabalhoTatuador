"""Cria (ou atualiza) um superusuário a partir de variáveis de ambiente.

Útil em plataformas sem shell interativo no plano grátis (ex.: Render), onde
não dá para rodar `createsuperuser` manualmente. É idempotente: pode rodar em
todo deploy sem quebrar o build.

Variáveis usadas:
- DJANGO_SUPERUSER_USERNAME (obrigatória para agir)
- DJANGO_SUPERUSER_PASSWORD (obrigatória para agir)
- DJANGO_SUPERUSER_EMAIL   (opcional)

Se usuário ou senha não estiverem definidos, o comando apenas avisa e sai sem erro.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria/atualiza um superusuário a partir de variáveis de ambiente (idempotente).'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write(
                'DJANGO_SUPERUSER_USERNAME/PASSWORD não definidos; nada a fazer.'
            )
            return

        user, created = User.objects.get_or_create(
            username=username, defaults={'email': email}
        )
        if email:
            user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        acao = 'criado' if created else 'atualizado'
        self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" {acao}.'))
