# purchase_procuration_multi_level
Extension to odoo/ocb provides multi level procuration to the purchase module.

Objective.
This module comes in handy when many users in an organisation are allowed to purchase products or services for varying limited amounts and you want a superior to confirm who may be limited as well.

Workflow Odoo.
Some users are allowed to create requests for purchase (RFFQ). When the RFQ is completed and confirmed it is turned into a purchase order. Each product can be assigned a different cost center.

Modification.
Per user and cost center a procuration rule with a limit and a superior can be defined. Some people (especially the managing director) may need several rules.
When a quotation (concerning only one cost center) is confirmed it will remain in it's state when the total amount exceeds the creator's procuration limit. First when a superior with a high enough limit confirms the quotation becomes a purchase order. It's possible to bypass a superior. All confirmations are registered as well as the next to confirm (even if he is bypassed).
Superiors can easily select all the RFQ's to confirm through a fiter or a single one by name.
