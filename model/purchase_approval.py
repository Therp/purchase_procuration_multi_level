# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.osv import fields


class purchase_approval(orm.Model):
    _name = "purchase.approval"
    _description = "Purchase approval"
    _columns = {
        "write_date":fields.datetime(string="Date modified", readonly = True,),
        "order_id": fields.many2one("purchase.order", "Order Reference",
                                    select = True, required = True,
                                    ondelete = "cascade"),
        "user_id": fields.many2one("res.users", "User", required = True),
        "approved": fields.boolean("Approved", required = True),
    }
    _order = "order_id"
