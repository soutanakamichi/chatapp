from django.contrib import admin

from .models import Talk, User  # Talk を追加

admin.site.register(User)
admin.site.register(Talk)