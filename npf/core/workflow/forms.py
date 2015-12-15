from django import forms

from npf.contrib.common.forms import RequiredInlineFormSet
from npf.core.workflow.models import WorkflowMemo


class WorkflowMemoAdminForm(forms.ModelForm):

    class Meta:
        model = WorkflowMemo
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        deadline = cleaned_data.get('deadline')

        if deadline and deadline < due_date:
            self.add_error(
                'deadline',
                'Крайний срок исполнения должен быть равен или позднее срока исполнения.'
            )

        return cleaned_data


class ParticipantInlineFormset(RequiredInlineFormSet):

    def clean(self):
        if any(self.errors):
            return

        current = self.instance.current_participant
        complete = self.instance.complete

        if all([form.cleaned_data['DELETE'] for form in self.forms]):
            raise forms.ValidationError('Должен быть как мининмум один участник')

        if len(self.forms) < 1:
            raise forms.ValidationError('Добавьте как мининмум одного участника')

        if current and current.user == self.user:
            for form in self.forms:
                if form.instance.user == self.user and complete:
                    if not form.cleaned_data['spent']:
                        form.add_error(
                            'spent',
                            'Укажите затраченное время.'
                        )
                else:
                    if form.has_changed() and 'spent' in form.changed_data:
                        form.add_error(
                            'spent',
                            'Нельзя изменять затраченное время других участников.'
                        )
