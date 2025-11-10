from django.contrib import admin
from .models import Subject, Notes, Flashcard_set, Flashcard, Activity, User_activity, Status, Flashcard_rating

# Register your models here.

admin.site.register(Subject)
admin.site.register(Notes)
admin.site.register(Flashcard_set)
admin.site.register(Flashcard)
admin.site.register(Activity)
admin.site.register(User_activity)
admin.site.register(Status)
admin.site.register(Flashcard_rating)