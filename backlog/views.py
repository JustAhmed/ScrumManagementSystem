from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, FormView, View
from django.contrib.auth import get_user_model, login, authenticate
from django.utils.http import is_safe_url
from .forms import NewSprint, NewBackLog, NewTask, LoginForm, RegisterForm, TaskModificationForm
from django.contrib.auth.decorators import login_required
from django import template
from .models import UserManager
from .models import BackLog, Sprint, Task
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage


register = template.Library()

User = get_user_model()


@register.filter()
def lookup(d, key):
    return d[key]


class RequestFormAttachMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RequestFormAttachMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class NextUrlMixin(object):
    default_next = "/"

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        return self.default_next


# Create your views here.

@login_required
def home(request):
    backlogs = BackLog.objects.all()
    li = []
    for backlog in backlogs:
        counter = 0
        for sprint in backlog.sprints.all():
            counter += sprint.tasks.all().count()
        li.append(counter)
    return render(request, 'home.html', {'backlogs': backlogs, 'li': li, 'request': request})


@login_required
def backlog_sprints(request, pk):
    backlog = get_object_or_404(BackLog, pk=pk)
    sprints = backlog.sprints.all()
    can_add = True
    for i in sprints:
        if i.state != 3:
            can_add = False
            break
    return render(request, 'sprint.html', {'backlog': backlog, 'request': request, 'can_add': can_add})


@login_required
def new_sprint(request, pk):
    backlog = get_object_or_404(BackLog, pk=pk)
    if request.method == 'POST':
        sprint = Sprint.objects.create(
            name=request.POST['name'],
            backlog=backlog,
            end_at=request.POST['dead_line']
        )
        return redirect('backlog_sprints', pk=backlog.pk)
    return render(request, 'new_sprint.html', {'backlog': backlog, 'form': NewSprint})


@login_required
def new_task(request, pk, spk):
    backlog = get_object_or_404(BackLog, pk=pk)
    sprint = get_object_or_404(Sprint, pk=spk)
    if request.method == 'POST':
        end_at = request.POST['dead_line']
        if request.POST['dead_line'] > str(sprint.end_at):
            end_at = sprint.end_at
        task = Task.objects.create(
            name=request.POST['name'],
            sprint=sprint,
            description=request.POST['description'],
            end_at=end_at,
            importance=request.POST['importance'],
            assigned_user=None

        )
        return redirect('sprint_tasks', pk, spk)
    return render(request, 'new_task.html', {'backlog': backlog, 'sprint': sprint, 'form': NewTask})


@login_required
def new_backlog(request):
    if request.method == 'POST':
        backlog = BackLog.objects.create(
            name=request.POST['name'],
            end_at=request.POST['dead_line'],
        )
        return redirect('home')
    return render(request, 'new_backlog.html', {'form': NewBackLog})


@login_required
def sprint_tasks(request, pk, spk):
    backlog = get_object_or_404(BackLog, pk=pk)
    sprint = get_object_or_404(Sprint, pk=spk)
    unsorted_tasks = sprint.tasks.all()
    all_tasks = unsorted_tasks
    sort_type = request.POST.get('drop_down')
    if sort_type is 1:
        imp = True
    else:
        imp = False
    qs1 = sprint.tasks.filter(status=1)
    qs2 = sprint.tasks.filter(status=2)
    all_done = True
    if len(qs2) > 0 and len(qs1) > 0:
        all_done = False
    if request.method == 'POST':
        try:
            helper = request.POST.get('start_sprint')
            if helper == "start":
                sprint.state = 2
                sprint.save()
                return render(request, "task.html", {'backlog': backlog, 'sprint': sprint,
                                                     'request': request, 'all_tasks': all_tasks, 'imp': imp})

            selected_task = sprint.tasks.get(pk=request.POST['task'])
            if selected_task.status == 2 and selected_task.assigned_user == request.user and request.user.is_admin:
                selected_task.status = 3
            elif selected_task.status == 2 and not request.user.is_admin:
                selected_task.status = 3
            elif not selected_task.assigned_user:
                selected_task.assigned_user = request.user
                selected_task.status = 2
            else:
                selected_task.assigned_user = None
                selected_task.status = 1

            selected_task.save()
            qs1 = sprint.tasks.filter(status=1)
            qs2 = sprint.tasks.filter(status=2)
            if len(qs2) > 0 and len(qs1) > 0:
                all_done = False
            else:
                all_done = True
            if all_done:
                sprint.state = 3
                sprint.save()
        except (KeyError, Task.DoesNotExist):
            if sort_type is '1':
                all_tasks = sprint.tasks.order_by('importance')
                imp = True
            elif sort_type is '2':
                all_tasks = sprint.tasks.order_by('end_at')
                imp = False

        return render(request, "task.html", {'backlog': backlog, 'sprint': sprint,
                                             'request': request, 'all_tasks': all_tasks, 'imp': imp})

    if request.method == 'GET':
        return render(request, 'task.html', {'backlog': backlog, 'sprint': sprint,
                                             'request': request, 'all_tasks': all_tasks, 'imp': imp})


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/home'
    template_name = 'login.html'
    default_next = '/home'

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)


# class RegisterView(CreateView):
#    form_class = RegisterForm
#    template_name = 'register.html'
#    success_url = '/'

def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        object = UserManager()
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.object.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for the confirmation. Now you can <a href="/">login</a> your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def modify_task(request, pk, spk):
    backlog = get_object_or_404(BackLog, pk=pk)
    sprint = get_object_or_404(Sprint, pk=spk)
    selected_task = sprint.tasks.get(pk=request.GET['task'])

    if request.method == 'POST' and request.user.is_admin:
        form = TaskModificationForm(request.POST)

        if form.is_valid():
            object = UserManager()
            if request.POST['dead_line'] > str(sprint.end_at):
                selected_task.end_at = sprint.end_at
            else:
                selected_task.end_at = request.POST['dead_line']
            selected_task.name = request.POST['name']
            selected_task.description = request.POST['description']
            selected_task.importance = request.POST['importance']
            # selected_task.assigned_user = request.POST['assigned_user']
            selected_task.assigned_user = User.object.all().get(email=request.POST['assigned_user'])
            if selected_task.assigned_user:
                selected_task.status = 2
            selected_task.save()
            return redirect('sprint_tasks', pk, spk)
    else:
        form = TaskModificationForm(initial={'name': selected_task.name,
                                             'description': selected_task.description,
                                             'dead_line': selected_task.end_at,
                                             'importance': selected_task.importance,
                                             'assigned_user': selected_task.assigned_user})
            
    return render(request, 'modify.html', {'task': selected_task, 'sprint': sprint, 'form': form})


class AboutPage(View):
    def get(self, request):
        return render(request, 'about.html')