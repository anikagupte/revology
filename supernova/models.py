from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Subject(models.Model):
   name = models.CharField(max_length=200, unique=True)

   def  __str__(self):
        return self.name


class Notes(models.Model):
    notes_content = models.TextField()
    # include images and document formatting
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_notes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    date_uploaded = models.DateTimeField('date uploaded', auto_now_add=True)
    image = models.ImageField(null=True, blank=True)

    def  __str__(self):
        return f'{self.id}: {self.title} ({self.subject})'
    
    def preview_note(self, num):
        preview = ""
        if len(self.notes_content) > num:
            for i in range(num):
                preview += self.notes_content(i)
            return preview
        else:
            return self.notes_content


class Flashcard_set(models.Model):
    title = models.CharField(max_length=30)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def  __str__(self):
        return f'{self.id}: {self.title} ({self.subject})'


class Flashcard(models.Model):
    front_of_card = models.TextField(max_length=2000)
    back_of_card = models.TextField(max_length=2000)
    flashcard_set = models.ForeignKey(Flashcard_set, on_delete=models.CASCADE, related_name='flashcards')
    date_created = models.DateTimeField('date created', auto_now_add=True)

    def  __str__(self):
        return f'{self.id}: {self.flashcard_set.title} ({self.flashcard_set.id})'
    
    def get_rag(self, user):
        try:
            return Flashcard_rating.objects.filter(flashcard=self, user=user)[0].status.colour
        except IndexError:
            return Status.red

class Status(models.Model):
    red = 'R'
    amber = 'A'
    green = 'G'
    STATUS_CHOICES = {
        red: "red flashcard",
        amber: "amber flashcard",
        green: "green flashcard"
    }
    colour = models.CharField(max_length=1, choices=STATUS_CHOICES, primary_key=True)

    def  __str__(self):
        return self.colour


class Flashcard_rating(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.flashcard.id} / {self.user.username} / {self.status.colour}"
    


class Activity(models.Model):
    open_notes = "ON"
    open_flashcards = "OF"
    create_notes = "CN"
    create_flashcards = "CF"
    edit_todo = "ET"
    ACTIVITY_CHOICES = {
        open_notes: "clicking a url for a notes document",
        open_flashcards: "clicking a url for a flashcard set",
        create_notes: "saving a new notes document to the library",
        create_flashcards: "saving a flashcard set to the collection",
        edit_todo: "editing the user's todo list",
    }
    name = models.CharField(max_length=2, choices=ACTIVITY_CHOICES)

    def  __str__(self):
        return self.name


class User_activity(models.Model):
    activity_type = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('date of activity', auto_now_add=True)

    def  __str__(self):
        return f'{self.user}: {self.activity_type}'