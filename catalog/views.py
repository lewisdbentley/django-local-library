from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required


# Create your views here.

from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.count()
    num_books_with_the_in_title = Book.objects.filter(title__icontains='the').count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_the_in_title': num_books_with_the_in_title,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

from django.db.models import Count

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """
        Override get_context_data to add
        other variables to the context.
        """
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['author_list'] = Author.objects.annotate(
                                    num_books=Count('book')
                                )
        return context

class BookDetailView(generic.DetailView):
    model = Book
    
class AuthorDetailView(generic.DetailView):
    model = Author

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class BorrowedBooksListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing all books on loan."""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm, RenewBookModelForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

#################
# AUTHOR C(R)UD #
#################

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Author
    success_url = reverse_lazy('authors')

#################
#  BOOK C(R)UD  #
#################

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Book
    fields = '__all__'
    initial = {'summary': 'some book'}

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_create_update_destroy'
    model = Book
    success_url = reverse_lazy('books')

#################
#INSTANCE C(R)UD#
#################

class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = BookInstance
    fields = '__all__'
    initial = {'due_back': '11/10/1990'}

class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_create_update_destroy'
    model = BookInstance
    fields = '__all__'

class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_create_update_destroy'
    model = BookInstance
    success_url = reverse_lazy('books')