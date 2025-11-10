from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import Subject, Notes, Flashcard_set, Flashcard, Status, Flashcard_rating


def homepage(request):

    # find user
    profile = User.objects.get(username=request.user)

    # collect notes + flashcards which the user has created
    nts = Notes.objects.filter(author=profile).order_by('-date_uploaded')
    fcs = Flashcard_set.objects.filter(author=profile).order_by('-date_created')

    return render(request, "supernova/homepage.html", {'user_notes': nts, 'user_flashcards': fcs})


def signup(request):

    if request.method == 'POST':

        # create a new user
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
        login(request, user)

        return redirect('supernova:homepage')

    else:
        return render(request, "supernova/signup.html")
    

def log_in(request):

    # log user into website
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # check if credentials are correct
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('supernova:homepage')
    else:
        return render(
            request,
            "supernova/login.html",
            {
                "error_message": "Incorrect login details",
            },
        )


def log_out(request):
    logout(request)
    return redirect('supernova:login')


def notes_library(request):
    return render(request, "supernova/notes_library.html", {'subjects': Subject.objects.all()})


def subject_notes(request, subject_name):

    # display notes of one subject
    subject = get_object_or_404(Subject, name=subject_name)
    return render(request, "supernova/subject_notes.html", {'subject': subject, 'notes': subject.notes_set.order_by('-date_uploaded')})


def create_notes(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        s = request.POST.get('subject', '').title()
        notes = request.POST.get('notes_content', '')
        f = request.FILES.get('noteimage', None)

        # ensure title and subject is not left blank
        if not (s.strip() and notes.strip() and title.strip()):
            return render(request, 'supernova/create_notes.html', {'error': 'Field is empty. Please fill in every field.'}) 

        # check if subject exists, else create a new one
        try:
            subject = Subject.objects.get(name=s)
        except Subject.DoesNotExist:
            subject = Subject(name=s)
            subject.save()
        
        # create a new notes document
        if f:
            n = Notes(notes_content=notes, author=request.user, subject=subject, title=title, image=f)
        else:
            n = Notes(notes_content=notes, author=request.user, subject=subject, title=title)
        n.save()

        return redirect('supernova:view_note', note_id=n.id)
    return render(request, 'supernova/create_notes.html')


def edit_notes(request, noteid):
    n = Notes.objects.get(id=noteid)
    if request.user == n.author:
        if request.method == 'POST':
            title = request.POST.get('title', '')
            s = request.POST.get('subject', '').title()
            notes = request.POST.get('notes_content', '')
            f = request.FILES.get('noteimage', None)

            # ensure title and subject is not left blank
            if not (s.strip() and notes.strip() and title.strip()):
                return render(request, 'supernova/create_notes.html', {'error': 'Field is empty. Please fill in every field.'}) 

            # check if subject exists, else create a new one
            try:
                subject = Subject.objects.get(name=s)
            except Subject.DoesNotExist:
                subject = Subject(name=s)
                subject.save()
            
            # edit notes document
            n = Notes.objects.get(id=noteid)
            n.notes_content = notes
            n.subject = subject
            n.title = title
            if f:
                n.image = f
            n.save()

            return redirect('supernova:view_note', note_id=n.id)
        return render(request, "supernova/edit_notes.html", {'note': n})
    else:
        return render(request, "supernova/note.html", {'note': n})


def view_note(request, note_id):
    note = Notes.objects.get(id=note_id)
    return render(request, "supernova/note.html", {'note': note})


def flashcard_set(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        s = request.POST.get('subject', '').title()

        # ensure title and subject is not left blank
        if not (s.strip() and title.strip()):
            return render(request, 'supernova/flashcard_set.html', {'error': 'Field is empty. Please fill in every field.'}) 

        # check if subject exists, else create a new one
        try:
            subject = Subject.objects.get(name=s)
        except Subject.DoesNotExist:
            subject = Subject(name=s)
            subject.save()
        
        # create a new flashcard set
        fcs = Flashcard_set(title=title, author=request.user, subject=subject)
        fcs.save()

        return redirect('supernova:view_flashcards', flashcardset_id=fcs.id)

    return render(request, "supernova/flashcard_set.html")


def view_flashcards(request, flashcardset_id):
    fcs = Flashcard_set.objects.get(id=flashcardset_id)

    if request.user == fcs.author and request.method == 'POST':

        # allow user to create new flashcards if they are the author of that set
        front = request.POST.get('front_of_card', '')
        back = request.POST.get('back_of_card', '')
        flashcard = Flashcard(front_of_card=front, back_of_card=back, flashcard_set=fcs)
        flashcard.save()

        # set default rank as red
        s = Status(colour="R")
        ranking = Flashcard_rating(user=request.user, flashcard=flashcard, status=s)
        ranking.save()

        return redirect(request.META['HTTP_REFERER'])
    
    return render(request, 'supernova/view_flashcards.html', {'fcs': fcs})


def browse_flashcards(request):

    # all flashcard sets
    fcs = Flashcard_set.objects.order_by('-date_created')

    # only flashcard sets created by the user
    user_fcs = Flashcard_set.objects.filter(author=request.user).order_by('-date_created')
    return render(request, "supernova/browse_flashcards.html", {'flashcards': fcs, 'user_flashcards': user_fcs})


def rag(request, cardid):
    
    # update rank of flashcard
    rank = request.GET['rank']
    s = Status.objects.get(colour=rank)
    fc = Flashcard.objects.get(id=cardid)
    try:
        ranking = Flashcard_rating.objects.get(user=request.user, flashcard=fc)
        ranking.status = s
        ranking.save()
    except Flashcard_rating.DoesNotExist:
        ranking = Flashcard_rating(user=request.user, flashcard=fc, status=s)
        ranking.save()

    return redirect(request.META['HTTP_REFERER'])


def user_profile(request, user):

    # find user
    profile = User.objects.get(username=user)

    # collect notes + flashcards which the user has created
    nts = Notes.objects.filter(author=profile).order_by('-date_uploaded')
    fcs = Flashcard_set.objects.filter(author=profile).order_by('-date_created')

    return render(request, "supernova/user_profile.html", {'user': profile, 'notes': nts, 'flashcards': fcs})


STOP_WORDS = [
    # articles
    "a","an","the",
    # coordination / subordination
    "and","or","but","nor","so","yet","for","if","than","that","because","while","although","though","unless","until","since","when","where","whether",
    # common prepositions
    "of","in","on","at","by","to","from","into","onto","over","under","about","with","without","within","between","through","across","after","before","during","against","per","as",
    # pronouns/determiners often not helpful for search
    "i","you","he","she","it","we","they","me","him","her","us","them","my","your","his","its","our","their","this","that","these","those",
    # misc
    "is","am","are","was","were","be","been","being","do","does","did","doing","not","no","yes"
    ]


from django.db.models import Q
def notes_search(request):

    # get search results
    searched = request.GET.get('search', '')
    if not searched:
        return redirect(request.META['HTTP_REFERER'])

    search = searched.split()

    search = [word for word in search if word.strip() and word not in STOP_WORDS]

    # check user did not submit a blank search
    if not search:
        return redirect(request.META['HTTP_REFERER'])

    query = Q()

    for word in search:
        # search through both the title and content of each note
        query |= Q(notes_content__icontains=word) | Q(title__icontains=word)

    results = Notes.objects.filter(query).distinct()

    return render(request, "supernova/search.html", {'results': results})


def fcs_search(request):

    # get search results
    searched = request.GET.get('search', '')
    if not searched:
        return redirect(request.META['HTTP_REFERER'])
    
    search = searched.split()

    search = [word for word in search if word.strip() and word not in STOP_WORDS]

    # check user did not submit a blank search 
    if not search:
        return redirect(request.META['HTTP_REFERER'])
    
    title_results = Flashcard.objects.none()
    content_results = Flashcard.objects.none()

    for word in search:
        # search through all flashcard set titles
        title_results = title_results.union(Flashcard_set.objects.filter(title__icontains=word))
        # TODO: search through the content of each flashcard THIS DOES NOT WORK
        content_results = content_results.union(Flashcard_set.objects.filter(flashcards__in=Flashcard.objects.filter(Q(front_of_card__icontains=word) | Q(back_of_card__icontains=word))))

    return render(request, "supernova/fcs_search.html", {'title_results': title_results.distinct(), 'content_results': content_results.distinct()})
# have an option to search for a user


def reset_ratings(request, fcs_id):

    # reset all ratings of a flashcard set back to red
    if request.method == "GET":
        s = Status.objects.get(colour='R')
        fcs = Flashcard_set.objects.get(id=fcs_id)
        for flashcard in fcs.flashcards.all():
            fc = Flashcard.objects.get(id=flashcard.id)
            ranking = Flashcard_rating.objects.get(user=request.user, flashcard=fc)
            ranking.status = s
            ranking.save()

    return redirect(request.META['HTTP_REFERER'])


def delete_fc(request, fc_id):

    # get flashcard
    fc = Flashcard.objects.get(id=fc_id)

    # delete flashcard
    fc.delete()

    return redirect(request.META['HTTP_REFERER'])


def filter_flashcards(request, colour):
    print(colour)
    return redirect(request.META['HTTP_REFERER'], {'colour': colour})


def resources(request):

    # open resources page
    return render(request, "supernova/resources.html",)


# TODO:
# finish flashcard filtering

# TODO v2:
# user activity tracking (streak?)
# link flashcards and notes
# homepage trending topics