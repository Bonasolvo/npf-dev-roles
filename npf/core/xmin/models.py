from mptt.models import MPTTModel, TreeForeignKey


class XminTreeModel(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class Meta:
        abstract = True
        ordering = ['tree_id', 'lft']