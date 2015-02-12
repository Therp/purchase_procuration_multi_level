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
from openerp.osv.orm import except_orm
from openerp.tools.translate import _


class res_procuration_limit_user(orm.Model):
    def create(self, cr, uid, vals, context=None):
        """ Before creation the final checks are to be performed """
        self.on_save(cr, uid, False, vals, context=context)
        return super(res_procuration_limit_user, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """ Before update the final checks are to be performed """
        for this_obj in self.browse(cr, uid, ids, context=context):
            self.on_save(cr, uid, this_obj, vals, context=context)
        super(res_procuration_limit_user, self).write(
            cr, uid, ids, vals, context=context)
        return True

    def on_save(self, cr, uid, this_obj, vals, context=None):
        """ On save the relations between several procuration rules
            are to be checked """
        this_id = []
        if this_obj:
            this_id.append(this_obj.id)
        user_id = (
            "user_id" in vals
            and vals.get("user_id")
            or this_obj and this_obj.user_id.id or False)
        analytic_id = (
            "analytic_id" in vals
            and vals.get("analytic_id")
            or this_obj and this_obj.analytic_id.id or False)
        procuration_limit_id = (
            "procuration_limit_id" in vals
            and vals.get("procuration_limit_id")
            or this_obj and this_obj.procuration_limit_id.id or False)
        user_manager_id = (
            "user_manager_id" in vals
            and vals.get("user_manager_id")
            or this_obj and this_obj.user_manager_id.id or False)
        """ Since it might happen that after changing a field a button is 
            pressed without activating the onchange action it needs be called
            """
        self.on_change(
            cr, uid, this_id,
            user_id, analytic_id, procuration_limit_id, user_manager_id,
            context=context)
        return True

    def on_change(
        self, cr, uid, ids,
        user_id, analytic_id, procuration_limit_id, user_manager_id,
            context=None):
        """ Onchange of some related fields checks are to be performed 
            and some values be set. """
        value = {}

        if procuration_limit_id and user_id:
            # exclude double limit for user_id/analytic_id
            if analytic_id:
                if self.search(
                    cr, uid, ['&', '&', '|',
                              ("analytic_id", "=", analytic_id),
                              ("analytic_id", "=", False),
                              ("user_id", "=", user_id),
                              ("id", "not in", ids)]):
                    raise except_orm(
                        _("Error"),
                        _("user already has a procuration limit \
                          for this cost center"))
            else:
                if self.search(
                    cr, uid, ['&',
                              ("user_id", "=", user_id),
                              ("id", "not in", ids)]):
                    raise except_orm(
                        _("Error"),
                        _("user already has a procuration limit"))

            cls_lmt = self.pool.get("res.procuration.limit")
            procuration_limit = cls_lmt.browse(
                cr, uid,
                procuration_limit_id, context=context).procuration_limit
            value["procuration_limit"] = procuration_limit
            higher_limits = cls_lmt.search(
                cr, uid, [("procuration_limit", ">", procuration_limit)])
            if higher_limits and not user_manager_id:
                raise except_orm(
                    _("Error"),
                    _("user should have a manager or \
                    the ultimate procuration limit for this cost center"))

            if user_manager_id:
                # this user has the highest limit possible
                if not higher_limits:
                    raise except_orm(
                        _("Error"),
                        _("user should not have a manager or not have \
                        the ultimate procuration limit for this cost center"))
                    return {"value": value}

                # has the manager a higher procuration_limit?
                if analytic_id:
                    if not self.search(
                        cr, uid,
                        ['&', '&',
                         ("analytic_id", "=", analytic_id),
                         ("user_id", "=", user_manager_id),
                         ("procuration_limit_id", "in", higher_limits)]):
                        raise except_orm(
                            _("Error"),
                            _("the manager should have a higher \
                            procuration limit for this cost center"))
                else:
                    if not self.search(
                        cr, uid,
                        [("user_id", "=", user_manager_id),
                         ("procuration_limit_id", "in", higher_limits)]):
                        raise except_orm(_("Error"),
                            _("the manager should have a higher \
                            procuration limit for this cost center"))

            # doesn't user manage users with same or higher procuration_limit?
            lower_limits = cls_lmt.search(cr, uid, [("procuration_limit", "<=",
                                                     procuration_limit)])
            if analytic_id:
                if self.search(
                    cr, uid, ['&', '&',
                              ("analytic_id", "=", analytic_id),
                              ("user_manager_id", "=", user_id),
                              ("procuration_limit_id",
                               "not in", lower_limits)]):
                    raise except_orm(
                        _("Error"),
                        _("user should have a higher procuration limit \
                          than all of his subordinates for this cost center"))
                mgr_proc_ids = self.search(
                    cr, uid, [("user_manager_id", "=", user_id), ])
                for proc_lim in self.browse(
                    cr, uid, mgr_proc_ids, context=context):
                    if not proc_lim.analytic_id:
                        raise except_orm(
                            _("Error"),
                            _("user's procuration is limited to some cost \
                              centers while one of his subordinates is not"))
            else:
                mgr_proc_ids = self.search(
                    cr, uid, ['&',
                              ("user_manager_id", "=", user_id),
                              ("procuration_limit_id",
                               "not in", lower_limits)])
                for proc_lim in self.browse(
                        cr, uid, mgr_proc_ids, context=context):
                    if not (proc_lim.analytic_id and not analytic_id
                            or proc_lim.analytic_id
                            and proc_lim.analytic_id.id == analytic_id):
                        raise except_orm(
                            _("Error"),
                            _("user should have a higher procuration limit \
                              than all of his subordinates \
                              for this cost center"))

        # all ok
        return {"value": value}

    def _procuration_limit(self, cr, uid, ids, field_name, arg, context=None):
        """ check if rfq is ready for next state. """
        result = {}
        for this_obj in self.browse(cr, uid, ids, context=context):
            result[this_obj.id] = {
                "procuration_limit":
                this_obj.procuration_limit_id.procuration_limit, }
        return result

    _name = "res.procuration.limit.user"
    _description = "user procuration limit"
    _columns = {
        "name": fields.char("Name", size=64, required=True,),
        "user_id": fields.many2one("res.users",
                                       "User", required=True,),
        "analytic_id": fields.many2one("account.analytic.account",
                                       "Cost center", required=True,),
        "procuration_limit_id": fields.many2one("res.procuration.limit",
                                       "Procuration limit", required=True,),
        "user_manager_id": fields.many2one("res.users", "Manager"),
        "procuration_limit": fields.function(_procuration_limit,
            multi="_procuration_limit",
            string="Procuration limit", type="float", digits=(16, 2),),
    }
    _order = "user_id, analytic_id"
