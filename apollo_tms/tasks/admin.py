from django.contrib import admin
from .models import Task, Collection, Assignment, RecurrentTask, OneTimeTask, DeadlineTask

# Register your models here.

#admin.site.register(Task)
admin.site.register(Collection)
admin.site.register(Assignment)
admin.site.register(RecurrentTask)
admin.site.register(OneTimeTask)
admin.site.register(DeadlineTask)