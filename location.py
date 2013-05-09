#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, In, Not

__all__ = ['Location']


class Location(ModelSQL, ModelView):
    __name__ = 'stock.location'

    warehouse = fields.Function(fields.Many2One('stock.location', 'Warehouse',
            on_change_with=['parent'],
            states={'invisible': Not(In(Eval('type'), ['storage', 'view']))},
            depends=['type']),
        'get_warehouse', searcher='search_warehouse')

    @classmethod
    def __setup__(cls):
        super(Location, cls).__setup__()
        cls._sql_constraints += [
            ('storage_location_unique', 'UNIQUE(storage_location)',
                'The Storage location must be unique.'),
            ]

    def on_change_with_warehouse(self, name=None):
        if (not self.id or self.type not in ('storage', 'view') or
                not self.parent):
            return None
        return self.parent.warehouse and self.parent.warehouse.id or None

    @classmethod
    def get_warehouse(cls, instances, name):
        warehouse_per_location = {}
        for warehouse in cls.search([('type', '=', 'warehouse')]):
            warehouse_per_location[warehouse.storage_location.id] = (
                warehouse.id)
        res = {}
        for location in instances:
            res[location.id] = None
            if location.type not in ('storage', 'view'):
                continue
            child_location_ids = []
            current_location = location
            while current_location:
                child_location_ids.append(current_location.id)
                if location.type not in ('storage', 'view'):
                    warehouse_per_location.update(
                        {}.fromkeys(child_location_ids, None))
                    break
                if current_location.id in warehouse_per_location:
                    warehouse_id = warehouse_per_location[current_location.id]
                    res[location.id] = warehouse_id
                    warehouse_per_location.update(
                        {}.fromkeys(child_location_ids, warehouse_id))
                    break
                current_location = current_location.parent
        return res

    @classmethod
    def search_warehouse(cls, name, clause):
        warehouse_child_locations = cls.search([
            ('parent.type', '=', 'warehouse'),
            ('type', '=', 'storage'),
            ('parent', clause[1], clause[2]),
            ])
        found_warehouse_ids = []
        storage_location_ids = []
        for location in warehouse_child_locations:
            if location.id != location.parent.storage_location.id:
                continue
            storage_location_ids.append(location.id)
            found_warehouse_ids.append(location.parent.id)

        warehouse_location_ids = []
        for location in cls.search([
                ('parent', 'child_of', storage_location_ids),
                ]):
            if location.warehouse.id in found_warehouse_ids:
                warehouse_location_ids.append(location.id)
        return [('id', 'in', warehouse_location_ids)]
