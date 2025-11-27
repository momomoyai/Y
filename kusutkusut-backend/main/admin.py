from django.contrib import admin
from .models import Person, Tweet

admin.site.register(Person)
admin.site.register(Tweet)