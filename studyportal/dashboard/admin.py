from django.contrib import admin
from .import models
from .models import *

# Register your models here.
admin.site.register(Notes)
admin.site.register(Homework)
admin.site.register(ToDo)