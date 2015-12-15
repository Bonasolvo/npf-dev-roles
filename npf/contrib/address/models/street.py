from .street_lazy import StreetLazy


class Street(StreetLazy):
    class Meta:
        db_table = 'zlk_street'
