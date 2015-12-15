from datetime import datetime

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from npf.core.workflow.utils import is_customer
from npf.core.workflow.models import Attachment, Participant, WorkflowMemo
from npf.core.workflow.forms import WorkflowMemoAdminForm, ParticipantInlineFormset
from npf.core.xmin.admin import XminAdmin, XminStackedInline


class AttachmentInline(XminStackedInline):

    model = Attachment
    fields = ['document']
    extra = 1
    columns = [{
        'dataIndex': 'document',
        'flex': 1,
    }]


class ParticipantInline(XminStackedInline):

    model = Participant
    formset = ParticipantInlineFormset
    extra = 1
    fields = ['user', 'role', 'spent', 'incoming_date', 'completion_date']
    readonly_fields = ['incoming_date', 'completion_date']
    columns = [{
        'dataIndex': 'user',
        'flex': 1,
    }, {
        'dataIndex': 'role',
        'flex': 1,
    }, {
        'dataIndex': 'spent',
        'flex': 1,
    }, {
        'dataIndex': 'incoming_date',
        'flex': 1,
    }, {
        'dataIndex': 'completion_date',
        'flex': 1,
    }]

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return self.extra

    def get_readonly_fields(self, request, obj=None):
        if is_customer(request.user, obj):
            return self.readonly_fields + ['spent']
        return self.readonly_fields + ['user', 'role']

    def get_formset(self, request, *args, **kwargs):
        formset = super().get_formset(request, *args, **kwargs)
        formset.user = request.user
        return formset

    def has_delete_permission(self, request, obj=None):
        if obj and request.user != obj.customer:
            return False
        return True

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and request.user != obj.customer:
            return 0
        return super().get_max_num(request, obj, **kwargs)


class WorkflowMemoAdmin(XminAdmin):

    list_display = ['title', 'task_type', 'due_date', 'status']
    list_filter = ['status', 'task_type']
    readonly_fields = ['status', 'created']
    participant_readonly_fields = [
        'process_instance', 'relatedmemos',
        'employment_rate', 'estimation', 'text', 'task_type', 'why_critical',
        'deadline', 'due_date', 'title'
    ]
    filter_horizontal = ['relatedmemos']
    inlines = [AttachmentInline, ParticipantInline]
    form = WorkflowMemoAdminForm
    columns = [{
        'dataIndex': 'title',
        'flex': 1,
    }, {
        'dataIndex': 'task_type',
        'flex': 1,
    }, {
        'dataIndex': 'due_date',
        'flex': 1,
    }, {
        'dataIndex': 'status',
        'flex': 1,
    }]

    def get_fields(self, request, obj=None):
        fields = super(WorkflowMemoAdmin, self).get_fields(request, obj)
        not_resolved = getattr(obj, 'status', '') != WorkflowMemo.Status.RESOLVED
        if is_customer(request.user, obj) and not_resolved:
            fields.pop(fields.index('complete'))
        if not obj:
            fields.pop(fields.index('created'))
        return fields

    def get_readonly_fields(self, request, obj=None):
        if is_customer(request.user, obj):
            return self.readonly_fields
        return self.readonly_fields + self.participant_readonly_fields

    def save_formset(self, request, form, formset, change):
        obj = formset.instance
        formset.save()
        if formset.prefix == 'participant_set':
            instances = self.get_formset_instances(formset)
            if not change:
                if instances:
                    self.add_memo(obj, instances[0], request.user)
            elif change and obj.complete:
                self.complete_memo(obj, instances)
            else:
                if obj.current_participant:
                    self.handle_current_deletion(instances, formset.deleted_objects, obj)

    def handle_current_deletion(self, participants, deleted, memo):
        deleted_users = [d.user for d in deleted]

        if memo.current_participant.user in deleted_users:
            memo.current_participant = None
            self.change_participant(participants, memo)
            memo.save()

    def get_formset_instances(self, formset):
        instances = list(getattr(formset, '_queryset', []))
        for item in formset.deleted_objects:
            instances.remove(item)
        for item in formset.new_objects:
            instances.append(item)
        return [i for i in instances if i.completion_date is None]

    def add_memo(self, memo, participant, customer):
        memo.customer = customer
        memo.current_participant = participant
        memo.save()
        participant.incoming_date = datetime.now()
        participant.save()

    def complete_memo(self, memo, participants):
        if memo.current_participant:
            self.update_participant(memo.current_participant, participants)
            self.change_participant(participants, memo)
        else:
            memo.status = WorkflowMemo.Status.CLOSED
        memo.save()

    def update_participant(self, current, participants):
        index = participants.index(current)
        participants[index].completion_date = datetime.now()
        participants[index].save()

    def change_participant(self, participants, memo):
        next_participant = self.get_next_participant(participants, memo.current_participant)
        if next_participant:
            next_participant.incoming_date = datetime.now()
            next_participant.save()
        else:
            memo.status = WorkflowMemo.Status.RESOLVED
        memo.current_participant = next_participant

    def get_next_participant(self, participants, current=None):
        index = participants.index(current) if current else -1
        try:
            return participants[index + 1]
        except IndexError:
            return None

    def get_queryset(self, request):
        qs = super(WorkflowMemoAdmin, self).get_queryset(request)
        q = Q(customer=request.user) | Q(current_participant__user=request.user)
        return qs.filter(q)

    def response_change(self, request, obj):
        completed = self.uncomplete_memo(obj)
        if completed and obj.customer != request.user and '_continue' in request.POST:
            return HttpResponseRedirect(reverse("admin:workflow_workflowmemo_changelist"))
        return super().response_change(request, obj)

    def uncomplete_memo(self, memo):
        complete = memo.complete
        if complete:
            memo.complete = False
            memo.save()
        return complete
