from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "supernova"
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("signup", views.signup, name="signup"),
    path("login", views.log_in, name="login"),
    path("logout", views.log_out, name="logout"),
    path("notes_library", views.notes_library, name="notes_library"),
    path("subject/<str:subject_name>/", views.subject_notes, name="subject_notes"),
    path("create_notes", views.create_notes, name="create_notes"),
    path("note/<int:note_id>", views.view_note, name="view_note"),
    path("flashcard_set/", views.flashcard_set, name="flashcard_set"),
    path("view_flashcards/<int:flashcardset_id>", views.view_flashcards, name="view_flashcards"),
    path("browse_flashcards", views.browse_flashcards, name="browse_flashcards"),
    path("rag/<int:cardid>", views.rag, name='rag'),
    path("notes_search", views.notes_search, name="notes_search"),
    path("fcs_search", views.fcs_search, name="fcs_search"),
    path("profile/<str:user>/", views.user_profile, name="user_profile"),
    path("resources", views.resources, name="resources"),
    path("reset_ratings/<int:fcs_id>", views.reset_ratings, name="reset_ratings"),
    path("edit_notes/<int:noteid>", views.edit_notes, name="edit_notes"),
    path("delete_fc/<int:fc_id>", views.delete_fc, name='delete_fc'),
    path("filter_flashcards/<str:colour>", views.filter_flashcards, name='filter_flashcards')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)