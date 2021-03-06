from .forms import *
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .views import back_button_page_context
from webinterface.email_sending import send_welcome_email, send_email_changed


class AdminUpdateView(UpdateView):
    form_class = AdminSettingsForm
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Admin-Einstellungen"
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context

    def get_object(self, queryset=None):
        return self.request.user


class ScheduleNewView(CreateView):
    form_class = ScheduleForm
    model = Schedule
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Erzeuge neuen Putzplan"
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context

    def form_valid(self, form):
        self.object = form.save()
        schedule_group = form.cleaned_data['schedule_group']
        for group in schedule_group:
            group.schedules.add(self.object)
        return HttpResponseRedirect(self.get_success_url())


class ScheduleUpdateView(UpdateView):
    form_class = ScheduleForm
    model = Schedule
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ändere Putzplan"
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        context['delete_button'] = {'text': "Lösche Putzplan",
                                    'url': reverse_lazy('webinterface:schedule-delete', kwargs={'pk': self.object.pk})}
        return context

    def form_valid(self, form):
        self.object = form.save()

        schedule_group = form.cleaned_data['schedule_group']
        for group in schedule_group:
            group.schedules.add(self.object)

        return HttpResponseRedirect(self.get_success_url())


class ScheduleDeleteView(DeleteView):
    model = Schedule
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_delete_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Putzplan"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context


class ScheduleGroupNewView(CreateView):
    form_class = ScheduleGroupForm
    model = ScheduleGroup
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Erstelle eine neue Putzplan-Gruppierung"
        context['info_banner'] = {'text': "Putzplan-Gruppen vereinen Putzer mit Putzplänen und bestimmen, welche "
                                          "Gruppe an Putzern für welche Putzpläne zuständig sind. <br>"
                                          "Die 'Mitgliedschaft' in Putzplan-Gruppen wird über die Zugehörigkeiten "
                                          "der Putzer geregelt."}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:admin')}
        return context


class ScheduleGroupUpdateView(UpdateView):
    form_class = ScheduleGroupForm
    model = ScheduleGroup
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ändere eine Putzplan-Gruppierung"
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:admin')}
        context['delete_button'] = {'text': "Lösche Putzgruppe",
                                    'url': reverse_lazy('webinterface:schedule-group-delete',
                                                        kwargs={'pk': self.object.pk})}
        return context


class ScheduleGroupDeleteView(DeleteView):
    model = ScheduleGroup
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_delete_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Putzgruppe"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context


class CleanerNewView(CreateView):
    form_class = CleanerForm
    model = Cleaner
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Füge neuen Putzer hinzu"
        context['info_banner'] = {'text': "Bitte beachten: Der Putzer, den du jetzt erstellst, "
                                          "wird zunächst unter \"ausgezogen\" aufgelistet sein. <br>"
                                          "Um den Putzer zu \"aktivieren\", muss zunächst seine Zugehörigkeit "
                                          "festgelegt werden. <br>"
                                          "Das entsprechende Interface findest du im Reiter rechts vom Putzername "
                                          "unter <br>"
                                          "'<span class=\"glyphicon glyphicon-home\"></span> Zugehörigkeiten'."}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:admin')}
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.object.user.email = form.cleaned_data.get('email')
        self.object.user.save()

        send_welcome_email(self.object)
        return HttpResponseRedirect(self.get_success_url())


class CleanerUpdateView(UpdateView):
    form_class = CleanerForm
    model = Cleaner
    template_name = 'webinterface/generic_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.success_url = reverse_lazy('webinterface:admin')
        else:
            if 'cleaner_page' in kwargs:
                self.success_url = reverse_lazy('webinterface:cleaner', kwargs={'page': kwargs['cleaner_page']})
            else:
                self.success_url = reverse_lazy('webinterface:cleaner-no-page')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        if self.request.user.is_superuser or object.user.pk == self.request.user.pk:
            return object
        raise Http404("User doesn't match requested page")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ändere Putzerprofil"
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        if self.request.user.is_superuser:
            context['delete_button'] = {'text': "Lösche Putzer",
                                        'url': reverse_lazy('webinterface:cleaner-delete',
                                                            kwargs={'pk': self.object.pk})}
        return context

    def form_valid(self, form):
        previous_email = self.object.user.email
        self.object = form.save()
        if previous_email != form.cleaned_data.get('email'):
            self.object.user.email = form.cleaned_data.get('email')
            self.object.user.save()
            send_welcome_email(cleaner=self.object)
            send_email_changed(cleaner=self.object, previous_address=previous_email)
        return HttpResponseRedirect(self.success_url)


class CleanerDeleteView(DeleteView):
    model = Cleaner
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_delete_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Putzer"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context


class AffiliationNewView(CreateView):
    form_class = AffiliationForm
    model = Affiliation
    template_name = 'webinterface/affiliation_list.html'

    @staticmethod
    def info_text():
        return "<p><strong>Bitte beachten:</strong></p>" \
               "<p>Eine Änderung der Zugehörigkeiten eines " \
               "Putzers führt dazu, dass in den betroffenen Putzplänen die existierenden " \
               "Putzdienste im betroffenen Zeitraum auf <i>ungültig</i> " \
               "gesetzt werden und aktualisiert werden müssen.</p>" \
               "<p>Putzdienste in der jetzigen Woche oder in vergangenen Wochen bleiben " \
               "jedoch unberührt, falls sie nicht manuell gelöscht und neu erzeugt werden.</p>"

    def __init__(self):
        self.cleaner = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cleaner = Cleaner.objects.get(pk=kwargs['pk'])
        except Cleaner.DoesNotExist:
            raise Http404('Putzer, für den Zugehörigkeit geändert werden soll, existiert nicht!')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cleaner'] = self.cleaner
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            **context,
            **back_button_page_context(self.kwargs),
            'title': "Zugehörigkeiten von {}".format(self.cleaner.name),
            'submit_button': {'text': "Speichern"},
            'cancel_button': {'text': "Abbrechen",
                              'url': reverse_lazy('webinterface:affiliation-list',
                                                  kwargs={'pk': self.cleaner.pk})}, 'cleaner': self.cleaner,
            'info_banner': {'text': self.info_text()}
        }

        return context

    def form_valid(self, form):
        if 'pk' not in self.kwargs:
            raise Http404('No pk is supplied in AffiliationNewView!')
        try:
            cleaner = Cleaner.objects.get(pk=self.kwargs['pk'])
        except Cleaner.DoesNotExist:
            raise Http404('PK provided in URL does not belong to any Cleaner!')
        # self.object = form.save(commit=False)
        beginning_date = datetime.datetime.strptime(form.data['beginning'], "%d.%m.%Y")
        end_date = datetime.datetime.strptime(form.data['end'], "%d.%m.%Y")
        self.object = Affiliation(cleaner=cleaner,
                                  group=ScheduleGroup.objects.get(pk=form.data['group']),
                                  beginning=date_to_epoch_week(beginning_date),
                                  end=date_to_epoch_week(end_date))
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('webinterface:affiliation-list', kwargs={'pk': cleaner.pk}))


class AffiliationUpdateView(UpdateView):
    form_class = AffiliationForm
    model = Affiliation
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bearbeite Zugehörigkeit"
        context['info_banner'] = {
            'text': "<p>Du bearbeitest <strong>{}'s</strong> Zugehörigkeit in der "
                    "<strong>{}</strong> Putzgruppe, die am <strong>{}</strong> beginnt und am "
                    "<strong>{}</strong> endet.</p>".format(
                        self.object.cleaner, self.object.group,
                        self.object.beginning_as_date().strftime("%d. %b %Y"),
                        self.object.end_as_date().strftime("%d. %b %Y")) +
                    AffiliationNewView.info_text()}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:affiliation-list',
                                                        kwargs={'pk': self.object.cleaner.pk})}
        context['delete_button'] = {'text': "Lösche Zugehörigkeit",
                                    'url': reverse_lazy('webinterface:affiliation-delete',
                                                        kwargs={'pk': self.object.pk})}
        return context

    def form_valid(self, form):
        beginning_date = datetime.datetime.strptime(form.data['beginning'], "%d.%m.%Y")
        end_date = datetime.datetime.strptime(form.data['end'], "%d.%m.%Y")
        self.object.beginning = date_to_epoch_week(beginning_date)
        self.object.end = date_to_epoch_week(end_date)
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('webinterface:affiliation-list',
                                                 kwargs={'pk': self.object.cleaner.pk}))


class AffiliationDeleteView(DeleteView):
    model = Affiliation
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_delete_form.html'

    def get_success_url(self):
        return reverse_lazy('webinterface:affiliation-list', kwargs={'pk': self.object.cleaner.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Zugehörigkeit"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context

    # def delete(self, request, *args, **kwargs):
    #     affiliation = Affiliation.objects.get(pk=kwargs['pk'])
    #     self.success_url = reverse_lazy('webinterface:affiliation-list', kwargs={'pk': affiliation.cleaner.pk})
    #     return super().delete(request, *args, **kwargs)


class CleaningWeekUpdateView(UpdateView):
    form_class = CleaningWeekForm
    model = CleaningWeek
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Putzwoche deaktivieren"
        context['submit_button'] = {'text': "Speichern"}
        context['info_banner'] = {
            'text': "Du bearbeitest die Woche von <b>{}</b> bis <b>{}</b> im Putzplan <b>{}</b>".format(
                        self.object.week_start().strftime("%d. %b %Y"), self.object.week_end().strftime("%d. %b %Y"),
                        self.object.schedule, self.object.schedule.name)}
        return context

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy('webinterface:schedule',
                                                 kwargs={'slug': self.object.schedule.slug,
                                                         'page': self.kwargs['page']}))


class CleaningWeekDeleteView(DeleteView):
    model = CleaningWeek
    template_name = 'webinterface/generic_delete_form.html'

    def get_success_url(self):
        return reverse_lazy('webinterface:schedule', kwargs={'slug': self.object.schedule.slug,
                                                             'page': self.kwargs['page']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Putzwoche"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context


class AssignmentCreateView(FormView):
    template_name = 'webinterface/generic_form.html'
    form_class = AssignmentCreateForm

    def dispatch(self, request, *args, **kwargs):
        if 'schedule_pk' in kwargs:
            self.schedule = get_object_or_404(Schedule, pk=kwargs['schedule_pk'])
            self.success_url = reverse_lazy('webinterface:schedule', kwargs={'slug': self.schedule.slug,
                                                                             'page': kwargs['page']})
        else:
            self.schedule = None
            self.success_url = reverse_lazy('webinterface:admin')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'initial_begin' in self.kwargs and 'initial_end' in self.kwargs:
            kwargs['initial_begin'] = self.kwargs['initial_begin']
            kwargs['initial_end'] = self.kwargs['initial_end']
        if self.schedule:
            kwargs['initial_schedules'] = self.schedule
        else:
            kwargs['initial_schedules'] = Schedule.objects.enabled()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Erzeuge Putzdienste und aktualisiere Aufgaben"
        context['info_banner'] = {'text': "<p>Mit diesem Formular kannst du Putzdienste erzeugen und aktualisieren. "
                                          "Dabei werden auch die Aufgaben erzeugt bzw. aktualisiert. </p>"
                                          "<p>Folgendes geschieht im angegebenen Zeitraum "
                                          "in allen angekreuzten Putzdiensten: </p>"
                                          "<ul>"
                                          "<li>Fehlende Putzdienste werden neu erzeugt.</li>"
                                          "<li>Aufgaben werden aktualisiert.</li>"
                                          "<li>Ungültige Putzdienste werden gelöscht "
                                          "(Putzdienste werden auf ungültig gesetzt "
                                          "wenn wichtige Eigenschaften der Putzdienste verändert werden).</li>"
                                          "<li><strong>Gültige Putzdienste werden in Ruhe gelassen!</strong></li>"
                                          "</ul>"}
        context['submit_button'] = {'text': "Ausführen (Kann eine Weile dauern)"}
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.success_url}
        return context

    def form_valid(self, form):
        from_week = date_to_epoch_week(form.cleaned_data['from_date'])
        to_week = date_to_epoch_week(form.cleaned_data['to_date'])
        schedules = form.cleaned_data['schedules']
        for schedule in schedules:
            schedule.create_assignments_over_timespan(start_week=from_week, end_week=to_week)
        return HttpResponseRedirect(self.success_url)


class AssignmentUpdateView(UpdateView):
    form_class = AssignmentForm
    model = Assignment
    success_url = reverse_lazy('webinterface:admin')
    template_name = 'webinterface/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Einzelnen Putzdienst bearbeiten"
        context['info_banner'] = {'text': "Du bearbeitest einen einzelnen Putzdienst "
                                          "im Putzplan <strong>{}</strong> in der Woche von <strong>{}</strong> bis "
                                          "<strong>{}</strong>".format(
                                            self.object.schedule,
                                            self.object.cleaning_week.week_start().strftime("%d. %b %Y"),
                                            self.object.cleaning_week.week_end().strftime("%d. %b %Y"))}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:schedule',
                                                        kwargs={'slug': self.object.schedule.slug,
                                                                'page': self.kwargs['page']})}
        return context

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy('webinterface:schedule',
                                                 kwargs={'slug': self.object.schedule.slug,
                                                         'page': self.kwargs['page']}))


class TaskTemplateNewView(CreateView):
    form_class = TaskTemplateForm
    model = TaskTemplate
    template_name = 'webinterface/generic_form.html'

    def __init__(self):
        self.schedule = None
        self.object = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        try:
            self.schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        except Cleaner.DoesNotExist:
            raise Http404('Putzplan, für den eine Aufgabe erstellt werden soll, existiert nicht!')
        self.success_url = reverse_lazy('webinterface:schedule-task-list', kwargs={'pk': self.kwargs['pk']})
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['schedule'] = self.schedule
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Erstelle Aufgabe"
        context['info_banner'] = {'text': "<p>Diese Aufgabe gehört zum Putzplan <strong>{}</strong>, "
                                          "welcher sich jeden <strong>{}</strong> wiederholt.</p>"
                                          "<p><strong>Bitte beachten!</strong><br>"
                                          "Damit Putzer nicht durch kurzfristig neu erstellte Aufgaben überrascht "
                                          "werden, werden neue Aufgaben erst zu den Putzdiensten ab der "
                                          "nächsten Kalenderwoche hinzugefügt "
                                          "(KW beginnen immer am Montag).</p>"
                                          "<p>Soll dennoch ein früherer Putzdienst die neue Aufgabe erhalten, "
                                          "so gehe in der entsprechenden Putzwoche auf "
                                          "<span class=\"glyphicon glyphicon-cog\"></span> "
                                          "<span class=\"glyphicon glyphicon-menu-right\"></span>"
                                          "'<span class=\"glyphicon glyphicon-plus\"></span> "
                                          "Aufgaben aktualisieren'".format(
                                            self.schedule, Schedule.WEEKDAYS[self.schedule.weekday][1])}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context

    def form_valid(self, form):
        if 'pk' not in self.kwargs:
            raise Http404('No pk is supplied in TaskTemplateNewView!')
        try:
            schedule = Schedule.objects.get(pk=self.kwargs['pk'])
        except Schedule.DoesNotExist:
            raise Http404('PK provided in URL does not belong to any Schedule!')
        self.object = form.save(commit=False)
        self.object.schedule = schedule
        self.object.save()
        return HttpResponseRedirect(self.success_url)


class TaskTemplateUpdateView(UpdateView):
    form_class = TaskTemplateForm
    model = TaskTemplate
    template_name = 'webinterface/generic_form.html'

    def get_success_url(self):
        return reverse_lazy('webinterface:schedule-task-list', kwargs={'pk': self.object.schedule.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Bearbeite Aufgabe"
        context['info_banner'] = {'text': "Diese Aufgabe gehört zum Putzplan <strong>{}</strong>, "
                                          "welcher sich jeden <strong>{}</strong> wiederholt".format(
                                            self.object.schedule, Schedule.WEEKDAYS[self.object.schedule.weekday][1])}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': reverse_lazy('webinterface:schedule-task-list',
                                                        kwargs={'pk': self.object.schedule.pk})}
        context['delete_button'] = {'text': "Lösche Aufgabe",
                                    'url': reverse_lazy('webinterface:task-delete',
                                                        kwargs={'pk': self.object.pk})}
        return context


class TaskTemplateDeleteView(DeleteView):
    model = TaskTemplate
    template_name = 'webinterface/generic_delete_form.html'

    def get_success_url(self):
        return reverse_lazy('webinterface:schedule-task-list', kwargs={'pk': self.object.schedule.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Aufgabe"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context


class TaskCreateView(FormView):
    template_name = 'webinterface/generic_form.html'
    form_class = forms.Form

    def __init__(self):
        self.cleaning_week = None
        super().__init__()

    @staticmethod
    def create_ul_of_task_templates(templates):
        task_list = ['<li>' + x.name + '</li>' for x in templates]
        if len(task_list) == 0:
            return '<i>Keine Aufgaben</i>'
        return '<ul>' + ''.join(task_list) + '</ul>'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cleaning_week = CleaningWeek.objects.get(pk=kwargs['pk'])
        except Cleaner.DoesNotExist:
            raise Http404('Putzplan, für den Zugehörigkeit geändert werden soll, existiert nicht!')
        self.success_url = reverse_lazy('webinterface:schedule', kwargs={'slug': self.cleaning_week.schedule.slug,
                                                                         'page': kwargs['page']})
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cleaning_week'] = self.cleaning_week
        context['title'] = "Erzeuge Aufgaben für {} in der Woche von {} bis {}".\
            format(self.cleaning_week.schedule.name,
                   self.cleaning_week.week_start().strftime("%d. %b. %Y"),
                   self.cleaning_week.week_end().strftime("%d. %b. %Y"))

        missing_tasks = TaskCreateView.create_ul_of_task_templates(self.cleaning_week.task_templates_missing())

        context['info_banner'] = {'text': "<strong>Folgende Aufgaben wurden nachträglich erschaffen und "
                                          "deshalb nicht in diesen Putzdienst übernommen:</strong><br>"
                                          "{}".format(missing_tasks)}
        context['submit_button'] = {'text': "Fehlende Aufgaben erstellen"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context

    def form_valid(self, form):
        self.cleaning_week.create_missing_tasks()
        return HttpResponseRedirect(self.success_url)


class TaskCleanedView(UpdateView):
    form_class = TaskCleanedForm
    model = Task
    template_name = 'webinterface/generic_form.html'
    pk_url_kwarg = "task_pk"

    def __init__(self):
        self.assignment = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(Assignment, pk=kwargs['assignment_pk'])
        self.success_url = reverse_lazy('webinterface:assignment-tasks',
                                        kwargs={'cleaning_week_pk': self.assignment.cleaning_week.pk})
        try:
            self.cleaner = Cleaner.objects.get(user=self.request.user)
        except Cleaner.DoesNotExist:
            self.cleaner = None
            if not self.request.user.is_superuser:
                return HttpResponseForbidden("Kein Putzer ist mit deinem Nutzer verbunden.")

        if self.assignment.cleaner != self.cleaner and not self.request.user.is_superuser:
            return HttpResponseForbidden("Du bist nicht in der Liste erlaubter Putzer für diesen Putzdienst.")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            kwargs['logged_in_cleaner'] = Cleaner.objects.get(user=self.request.user)
        except Cleaner.DoesNotExist:
            kwargs['logged_in_cleaner'] = None

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Setze eine Aufgabe als 'geputzt'"
        context['info_banner'] = {'text': "<p><strong>Gespeicherter Hilfetext:</strong></p><p>" +
                                          self.object.template.help_text + "</p>"}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context


class DutySwitchNewView(CreateView):
    form_class = DutySwitchForm
    model = DutySwitch
    template_name = 'webinterface/generic_form.html'

    def __init__(self):
        self.assignment = None
        self.object = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        self.assignment = Assignment.objects.get(pk=self.kwargs['assignment_pk'])
        self.success_url = reverse_lazy('webinterface:cleaner', kwargs={'page': kwargs['page']})
        if DutySwitch.objects.filter(requester_assignment=self.assignment).exists():
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['requester_assignment'] = self.assignment
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Gib einen Putzdienst-Tausch in Auftrag"
        context['info_banner'] = {'text': "<p>Möchtest du deinen Putzdienst "
                                          "im Putzplan <b>{}</b> am <b>{}</b> tauschen?</p><br>"
                                          "<p><i>Wenn du den Putzdienst-Tausch in Auftrag gibst, wird auf der "
                                          "Startseite jeder Person, die mit dir tauschen kann, "
                                          "eine Nachricht eingeblendet. <br>"
                                          "Der Tausch erfolgt, wenn die Person eine ihrer Putzdienste "
                                          "zum Tauschen auswählt und den Tausch bestätigt.</i></p>"
                                          "<p>Bist du über eine längere Zeit nicht da oder ziehst du aus? "
                                          "Setze dich bitte mit dem Admin in Verbindung, damit er dich für die "
                                          "Zeit freistellen oder austragen kann!</p>".format(
                                            self.assignment.schedule,
                                            self.assignment.assignment_date().strftime("%d. %b %Y"))}
        context['submit_button'] = {'text': "Ja, ich möchte den Putzdienst-Tausch in Auftrag geben"}
        context['cancel_button'] = {'text': "Nein, hol mich hier raus!",
                                    'url': self.success_url}
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.requester_assignment = self.assignment
        self.object.save()
        # When setting commit=False in form.save(), you must call form.save_m2m() to save ManytoMany relationships!
        form.save_m2m()
        email_sending.send_email__dutyswitch_proposal(self.object)
        return HttpResponseRedirect(self.get_success_url())


class DutySwitchUpdateView(UpdateView):
    form_class = DutySwitchForm
    model = DutySwitch
    template_name = 'webinterface/generic_form.html'
    pk_url_kwarg = "dutyswitch_pk"

    def dispatch(self, request, *args, **kwargs):
        self.success_url = reverse_lazy('webinterface:cleaner', kwargs={'page': kwargs['page']})
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Ändere deine Putzdienst-Tausch Anfrage"
        context['info_banner'] = {
            'text': "<p>Du bearbeitest deine Putzdienst-Tausch Anfrage für deinen "
                    f"Dienst am {self.object.requester_assignment.assignment_date().strftime('%d. %b. %Y')}.</p>"
                    "<p>Andere Putzer werden nicht über deine Änderungen benachrichtigt.</p>"}
        context['submit_button'] = {'text': "Speichern"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        context['delete_button'] = {'text': "Tauschanfrage löschen",
                                    'url': reverse_lazy('webinterface:dutyswitch-delete',
                                                        kwargs={'pk': self.object.pk, 'page': self.kwargs['page']})}
        return context


class DutySwitchAcceptView(UpdateView):
    form_class = DutySwitchAcceptForm
    model = DutySwitch
    template_name = 'webinterface/generic_form.html'

    def __init__(self):
        self.cleaner = None
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        try:
            self.cleaner = Cleaner.objects.get(slug=request.user.username)
        except Cleaner.DoesNotExist:
            raise Http404('Du bist als ein Nutzer angemeldet, der keinem Putzer zugeordnet ist!')

        if 'page' in self.kwargs:
            self.success_url = reverse_lazy('webinterface:cleaner', kwargs={'page': self.kwargs['page']})
        else:
            self.success_url = reverse_lazy('webinterface:cleaner-no-page')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        if object.requester_assignment.cleaning_week.disabled:
            raise Http404('Der Putzdienst, der getauscht werden sollte, wurde zwischenzeitlich deaktiviert.')
        return object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cleaner'] = self.cleaner
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Tauschanfrage beantworten"
        context['info_banner'] = {'text': "<p><span class=\"glyphicon glyphicon-user\"></span> <strong>{}</strong> "
                                          "möchte seinen/ihren Dienst im Putzplan "
                                          "<span class=\"glyphicon glyphicon-list-alt\"></span> "
                                          "<strong>{}</strong> am "
                                          "<span class=\"glyphicon glyphicon-calendar\"></span> <strong>{} "
                                          "(in {} Tagen)</strong> tauschen.</p>"
                                          "<p><strong>Begründung</strong>:<br>{}</p>".format(
                                            self.object.requester_assignment.cleaner,
                                            self.object.requester_assignment.schedule,
                                            self.object.requester_assignment.assignment_date().strftime('%d. %b. %Y'),
                                            str((self.object.requester_assignment.assignment_date() -
                                                 timezone.now().date()).days),
                                            self.object.message)}
        context['submit_button'] = {'text': "Ja, tausche diese Putzdienste miteinander!"}
        context['cancel_button'] = {'text': "Abbrechen",
                                    'url': self.success_url}
        return context


class DutySwitchDeleteView(DeleteView):
    model = DutySwitch
    success_url = reverse_lazy('webinterface:cleaner')
    template_name = 'webinterface/generic_delete_form.html'

    def get_success_url(self):
        return reverse_lazy('webinterface:cleaner', kwargs={'page': self.kwargs['page']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lösche Tauschanfrage"
        context['cancel_button'] = {'text': "Abbrechen", 'url': self.get_success_url()}
        return context
