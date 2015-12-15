from django.contrib import admin

from npf.contrib.dict import models as dict
from .legal_form import LegalFormAdmin
from .document_type import DocumentTypeAdmin


admin.site.register(dict.LegalForm, LegalFormAdmin)
admin.site.register(dict.DocumentType, DocumentTypeAdmin)
