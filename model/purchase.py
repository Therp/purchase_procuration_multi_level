# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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


class purchase_order(orm.Model):
    """ a purchase order cannot become "approved" as long as it has not been
    confirmed by someone having enough procuration
    (the author or one of his superiors)"""
    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        """ When approving an order several check's are to be performed.
            The approval is to be registered as well as an eventually needed
            manager's approval. """
        result = False
        if not context:
            context = {}
        for po in self.browse(cr, uid, ids, context=context):
            app_cls = self.pool.get("purchase.approval")
            proc_cls = self.pool.get("res.procuration.limit.user")
            procuration_limit = self.get_procuration_limit(
                cr, uid, po.id, context=context)
            if not procuration_limit:
                # someone without procuration tries to approve
                raise except_orm(
                    _("Error"),
                    _("An in line manager of the creator of this \
                    quotation and for it's cost center should approve"))
            # update approver
            app_id = app_cls.search(
                cr, uid, ["&",
                          ("user_id", "=", uid),
                          ("order_id", "=", po.id), ])
            vals = {"approved": True, }
            if app_id:
                app_obj = app_cls.browse(cr, uid, app_id[0], context=context)
                if app_obj.approved:
                    raise except_orm(
                        _("Error"),
                        _("You already approved this quotation, \
                        an in line manager should approve too"))
                app_obj.write(vals, context=context)
            else:
                vals.update({"order_id": po.id, "user_id": uid, })
                app_cls.create(cr, uid, vals, context=context)
            # next to approve
            if po.amount_untaxed > procuration_limit:
                # find approver's manager
                proc_id = proc_cls.search(
                    cr, uid, ["&",
                              ("user_id", "=", uid),
                              ("analytic_id", "=", po.account_analytic_id.id),
                              ],)[0]
                proc_obj = proc_cls.browse(cr, uid, proc_id, context=context)
                vals = {"order_id": po.id,
                        "user_id": proc_obj.user_manager_id.id,
                        "approved": False}
                app_cls.create(cr, uid, vals, context=context)
            else:
                last_app_id = False
                validator_id = False
                for app in po.approval_ids:
                    if ((not last_app_id or last_app_id > app.id)
                            and app.approved):
                        last_app_id = app.id
                        validator_id = app.user_id.id
                result = (
                    super(purchase_order, self).wkf_confirm_order(
                        cr, uid, [po.id], context=context)
                    and self.write(
                        cr, uid, [po.id], {"validator": validator_id})
                    and super(purchase_order, self).wkf_approve_order(
                        cr, uid, [po.id], context=context))
            return result

    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Unlink approvals from cancelled order. """
        for po in self.browse(cr, uid, ids, context=context):
            super(purchase_order, self).action_cancel_draft(
                cr, uid, ids, context=context)
            self.unlink_approval(cr, uid, po.id, context=context)
        return True

    def purchase_cancel(self, cr, uid, ids, context=None):
        """ Unlink approvals from cancelled order. """
        for po in self.browse(cr, uid, ids, context=context):
            self.unlink_approval(cr, uid, po.id, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Unlink approvals from cancelled order. """
        for po in self.browse(cr, uid, ids, context=context):
            super(purchase_order, self).action_cancel(
                cr, uid, ids, context=context)
            self.unlink_approval(cr, uid, po.id, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        """ Unlink approvals from copied order. """
        order_id = super(purchase_order, self).copy(
            cr, uid, id, default, context)
        self.unlink_approval(cr, uid, order_id, context=context)
        return order_id

    def unlink_approval(self, cr, uid, id, context=None):
        """ Unlink_approvals. """
        app_cls = self.pool.get("purchase.approval")
        app_ids = app_cls.search(cr, uid, [("order_id", "=", id)],)
        app_cls.unlink(cr, uid, app_ids, context=context)

    def get_procuration_limit(self, cr, uid, id, context=None):
        """ Find out if uid = creator or in line manager of creator
        and if so return uid's procuration limit or raise error.
        """
        proc_cls = self.pool.get("res.procuration.limit.user")

        po = self.browse(cr, uid, id, context=context)

        creator = po.create_uid.id or uid
        proc_id = proc_cls.search(
            cr, uid, ["&",
                      ("user_id", "=", creator),
                      ("analytic_id", "=", po.account_analytic_id.id), ],)
        while proc_id:
            proc_obj = proc_cls.browse(cr, uid, proc_id[0], context=context)
            if proc_obj.user_id.id == uid:
                return proc_obj.procuration_limit_id.procuration_limit
            proc_id = proc_cls.search(
                cr, uid, ["&",
                          ("user_id", "=", proc_obj.user_manager_id.id),
                          ("analytic_id", "=", po.account_analytic_id.id), ],)
        return 0

    def write(self, cr, uid, ids, vals, context=None):
        """ Update purchase_order_line with account_analytic_id. """
        for this_obj in self.browse(cr, uid, ids, context=context):
            if ("account_analytic_id" in vals
                or "state" in vals
                    and vals.get("state") in {"confirmed", "approved"}):
                analytic_id = ("account_analytic_id" in vals
                and vals.get("account_analytic_id")
                    or this_obj.account_analytic_id.id)
                for line in this_obj.order_line:
                    line.write(
                        {"account_analytic_id": analytic_id}, context=context)
        super(purchase_order, self).write(cr, uid, ids, vals, context=context)
        return True

    def on_change_analytic_id(self, cr, uid, ids, analytic_id, context=None):
        value = {}

        if analytic_id:
            proc_cls = self.pool.get("res.procuration.limit.user")
            if not proc_cls.search(
                cr, uid, ["&",
                          ("user_id", "=", uid),
                          ("analytic_id", "=", analytic_id), ]):
                raise except_orm(
                    _("Error"),
                    _("You don't have a procuration limit \
                      for this cost center"))
        # all ok
        return {"value": value}

    def _allowed_analytic_ids(self, cr, uid, context=None):
        """ Select analytic_ids (cost centers) for which user has procuration.
        """
        analytic_ids = []
        proc_cls = self.pool.get("res.procuration.limit.user")
        proc_ids = proc_cls.search(cr, uid, [("user_id", "=", uid), ])
        if proc_ids:
            for proc in proc_cls.browse(cr, uid, proc_ids, context=context):
                analytic_ids.append(proc.analytic_id.id)
        else:
            analytic_ids = self.pool.get("account.analytic.account").search(
                cr, uid, [("type", "=", "normal"), ])
        return analytic_ids

    def _approval(self, cr, uid, ids, field_name, arg, context=None):
        """ Provide function fields. """
        result = {}
        for this_obj in self.browse(cr, uid, ids, context=context):
            analytic_ids = self._allowed_analytic_ids(cr, uid, context=context)
            res = self._approval_data(cr, uid, [this_obj.id], context=context)
            res.update({"allowed_analytic_ids": analytic_ids, })
            result[this_obj.id] = res
        return result

    def _approval_data(self, cr, uid, ids, context=None):
        """ Find last manager to approve and procuration_limit approved for.
        """
        proc_cls = self.pool.get("res.procuration.limit.user")
        approval_id = False
        user_approve_id = False
        app_date = False
        limit = 0.0
        for this_obj in self.browse(cr, uid, ids, context=context):
            for app_obj in this_obj.approval_ids:
                # user_approve_id
                if (not app_obj.approved
                        and (not app_date or app_date < app_obj.write_date)):
                    app_date = app_obj.write_date
                    user_approve_id = app_obj.user_id.id
                # approved_procuration_limit
                if (app_obj.approved):
                    proc_id = proc_cls.search(
                        cr, uid, ["&",
                                  ("user_id", "=", app_obj.user_id.id),
                                  ("analytic_id", "=",
                                   this_obj.account_analytic_id.id), ])
                    if proc_id:
                        his_limit = proc_cls.browse(
                            cr, uid, proc_id[0], context=context
                            ).procuration_limit_id.procuration_limit
                        if limit < his_limit:
                            limit = his_limit
                # approval_id
                approval_id = (
                    not this_obj.state == 'cancel'
                    and (this_obj.state == 'draft' or app_obj.approved)
                    and not app_obj.user_id.id == this_obj.validator.id
                    and app_obj.user_id.id
                    or approval_id)
        return {"user_approve_id": user_approve_id,
                "approved_procuration_limit": limit,
                "approval_id": approval_id}

    def _trigger_approval(self, cr, uid, ids, context=None):
        """ Find order_ids on change of purchase.approval. """
        result = []
        for this_obj in self.browse(cr, uid, ids, context=context):
            result.append(this_obj.order_id.id)
        return result

    _columns = {
        "account_analytic_id":
            fields.many2one("account.analytic.account", "Cost center",
            readonly=True,
            states={"draft": [("readonly", False)]},),
        "approval_ids":
            fields.one2many("purchase.approval", "order_id",
            "All next approvers",
            readonly=True, ondelete="set null",),
        "approval_id":
            fields.function(_approval, multi="_approval", method=True,
            type="many2one", relation="res.users",
            string="Approval by",),
        "user_approve_id":
            fields.function(_approval, multi="_approval", method=True,
            type="many2one", relation="res.users",
            string="Manager to approve",
            store={"purchase.approval":
                (_trigger_approval, ["approved"], 11)},),
        "approved_procuration_limit":
            fields.function(_approval, multi="_approval", method=True,
            type="float", digits=(16, 2),
            string="Procuration limit last approver",
            store={"purchase.approval":
                (_trigger_approval, ["approved"], 10)},),
        "allowed_analytic_ids":
            fields.function(_approval, multi="_approval", method=True,
            type="many2many", relation="account.analytic.account",
            string="Allowed cost centers",
            help="Cost centers for which user has procuration"),
    }
    _defaults = {
        "allowed_analytic_ids":
         lambda s, cr, uid, c: [(6, 0, s._allowed_analytic_ids(cr, uid, c))],
    }
