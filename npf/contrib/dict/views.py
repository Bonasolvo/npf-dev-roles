import json
from django.shortcuts import HttpResponse
from .models import *


def send_node_move(request):
    """
    Обработка изменения вложенности в древовидных справочниках
    """
    node_id = request.POST['node_id']
    new_parent_id = request.POST['new_parent_id']
    model = request.POST['model']
    model = eval(model + '.objects.get')

    if new_parent_id != 'root':
        new_parent = model(id=new_parent_id)
    else:
        new_parent = None

    node = model(id=node_id)
    node.move_to(new_parent, 'first-child')
    return HttpResponse(json.dumps({'success': True, 'result': 'ok'}), content_type='application/json')