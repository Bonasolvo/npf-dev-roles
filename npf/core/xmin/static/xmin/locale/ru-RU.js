Ext.define('Ext.locale.ru-RU.header.Container', {
    override: 'Ext.grid.header.Container',
    sortAscText: 'Сортировать по возрастанию',
    sortDescText: 'Сортировать по убыванию',
    sortClearText: 'Убрать сортировку',
    columnsText: 'Столбцы'
});

Ext.define('Ext.locale.ru-RU.view.AbstractView', {
   override: 'Ext.view.AbstractView',
   loadingText: 'Загрузка...'
});

Ext.define('Ext.locale.ru-RU.grid.filters.Filters', {
   override: 'Ext.grid.filters.Filters',
   menuFilterText: 'Фильтры'
});

Ext.define('Ext.locale.ru-RU.grid.filters.filter.String', {
   override: 'Ext.grid.filters.filter.String',
   emptyText: 'Введите текст фильтра...'
});

Ext.define('Ext.locale.ru-RU.grid.filters.filter.Number', {
   override: 'Ext.grid.filters.filter.Number',
   emptyText: 'Введите число...'
});

Ext.define('Ext.locale.ru-RU.grid.filters.filter.Boolean', {
   override: 'Ext.grid.filters.filter.Boolean',
   yesText: 'Да',
   noText: 'Нет'
});

Ext.define('Ext.locale.ru-RU.Date', {
    override: 'Ext.Date',
    dayNames: [
        'Воскресенье',
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота'
    ],
    monthNames: [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь'
    ]
});

Ext.define('Ext.locale.ru-RU.form.field.Date', {
   override: 'Ext.form.field.Date',
   format: django.formats['DATE_FORMAT'],
   submitFormat: 'Y-m-d',
   emptyText: "ДД.ММ.ГГГГ"
});

Ext.define('Ext.locale.ru-RU.form.field.Time', {
   override: 'Ext.form.field.Time',
   format: django.formats['TIME_FORMAT'],
   emptyText: "ЧЧ:ММ:СС"
});

Ext.define('Ext.locale.ru-RU.form.DateField', {
   override: 'Ext.form.DateField',
   disabledDaysText: "Не доступно",
   disabledDatesText: "Не доступно",
   minText: "Дата в этом поле должна быть позже {0}",
   maxText: "Дата в этом поле должна быть раньше {0}",
   invalidText: "{0} не является правильной датой - дата должна быть указана в формате {1}"
});

Ext.define('Ext.locale.ru-RU.picker.Date', {
    override: 'Ext.picker.Date',
    todayText: 'Сегодня',
    todayTip: '{0}',
    minText: "Эта дата раньше минимальной даты",
    maxText: "Эта дата позже максимальной даты",
    nextText: 'Следующий месяц (Control+Вправо)',
    prevText: 'Предыдущий месяц (Control+Влево)',
    monthYearText: 'Выбор месяца (Control+Вверх/Вниз для выбора года)',
    disabledDaysText: "",
    disabledDatesText: ""
});

Ext.define('Ext.locale.ru-RU.picker.Month', {
   override: 'Ext.picker.Month',
   cancelText: 'Отмена'
});


Ext.define('Ext.locale.ru-RU.grid.filters.filter.Date', {
    override: 'Ext.grid.filters.filter.Date',
    config: {
       fields: {
           lt: {text: 'До'},
           gt: {text: 'После'},
           eq: {text: '='}
       },
       dateFormat: 'Y-m-d'
   }
});

Ext.define('Ext.locale.ru-RU.PagingToolbar', {
    override: 'Ext.PagingToolbar',
    beforePageText: 'Страница',
    afterPageText: 'из {0}',
    firstText: 'Первая страница',
    prevText: 'Предыдущая страница',
    nextText: 'Следующая страница',
    lastText: 'Последняя страница',
    refreshText: 'Обновить страницу',
    displayMsg: 'Показано записей: {0} - {1} из {2}',
    emptyMsg: ''
});

Ext.define('Ext.locale.ru-RU.form.field.Text', {
    override: 'Ext.form.field.Text',
    blankText: 'Обязательное поле'
});

