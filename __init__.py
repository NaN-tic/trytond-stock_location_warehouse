#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from .location import Location


def register():
    Pool.register(
        Location,
        module='stock_location_warehouse', type_='model')
