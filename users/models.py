from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
	# inserir customizações
	birth_date = models.DateField(null=True, verbose_name="Data de Nascimento", help_text="Use o formato DD/MM/AAAA")

	def __str__(self):
		return self.username

# Create your models here.
