from npf.core.workflow.models import WorkflowTaskInstance

class WorkflowMyTaskInstance(WorkflowTaskInstance):
    """
    Прокси-модель: Экземпляр задачи. Используется для фильтрации всех задач по текущему пользователю и
    вывода списка "Мои задачи".
    """
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Мои задачи'
        proxy = True
