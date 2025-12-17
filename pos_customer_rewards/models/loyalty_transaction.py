# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class LoyaltyTransaction(models.Model):
    """Loyalty Transaction History.

    Immutable audit log of all point movements.
    Records cannot be modified or deleted after creation.
    """
    _name = 'loyalty.transaction'
    _description = 'Loyalty Transaction'
    _order = 'date desc, id desc'
    _rec_name = 'description'

    date = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        required=True,
        index=True,
        readonly=True,
        help="Date and time of the transaction.",
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True,
        index=True,
        readonly=True,
        ondelete='restrict',
        help="Customer who earned or redeemed points.",
    )
    program_id = fields.Many2one(
        comodel_name='loyalty.program',
        string="Loyalty Program",
        required=True,
        readonly=True,
        ondelete='restrict',
        help="Loyalty program for this transaction.",
    )

    # Transaction Details
    transaction_type = fields.Selection(
        selection=[
            ('earn', 'Points Earned'),
            ('redeem', 'Points Redeemed'),
            ('expire', 'Points Expired'),
            ('adjust', 'Manual Adjustment'),
        ],
        string="Type",
        required=True,
        readonly=True,
        help="Type of transaction.",
    )

    points = fields.Integer(
        string="Points",
        readonly=True,
        help="Points involved in this transaction. "
             "Positive for earned, negative for redeemed/expired.",
    )
    balance_after = fields.Integer(
        string="Balance After",
        readonly=True,
        help="Customer's points balance after this transaction.",
    )

    # References
    pos_order_id = fields.Many2one(
        comodel_name='pos.order',
        string="POS Order",
        readonly=True,
        ondelete='set null',
        help="Related POS order (if applicable).",
    )
    reward_id = fields.Many2one(
        comodel_name='loyalty.reward',
        string="Reward",
        readonly=True,
        ondelete='set null',
        help="Reward that was redeemed (if applicable).",
    )
    notes = fields.Text(
        string="Notes",
        readonly=True,
        help="Additional notes about this transaction.",
    )

    # Display
    description = fields.Char(
        string="Description",
        compute='_compute_description',
        store=True,
        help="Human-readable description of the transaction.",
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        related='program_id.company_id',
        store=True,
        readonly=True,
    )

    @api.depends('transaction_type', 'points', 'reward_id', 'pos_order_id')
    def _compute_description(self):
        """Generate human-readable description for the transaction."""
        for trans in self:
            if trans.transaction_type == 'earn':
                if trans.pos_order_id:
                    trans.description = _(
                        "Earned %(points)d points from order %(order)s",
                        points=trans.points,
                        order=trans.pos_order_id.name or trans.pos_order_id.pos_reference,
                    )
                else:
                    trans.description = _("Earned %(points)d points", points=trans.points)
            elif trans.transaction_type == 'redeem':
                if trans.reward_id:
                    trans.description = _(
                        "Redeemed %(points)d points for %(reward)s",
                        points=abs(trans.points),
                        reward=trans.reward_id.name,
                    )
                else:
                    trans.description = _(
                        "Redeemed %(points)d points",
                        points=abs(trans.points),
                    )
            elif trans.transaction_type == 'expire':
                trans.description = _(
                    "%(points)d points expired",
                    points=abs(trans.points),
                )
            elif trans.transaction_type == 'adjust':
                if trans.points >= 0:
                    trans.description = _(
                        "Manual adjustment: +%(points)d points",
                        points=trans.points,
                    )
                else:
                    trans.description = _(
                        "Manual adjustment: %(points)d points",
                        points=trans.points,
                    )
            else:
                trans.description = _("Transaction: %(points)d points", points=trans.points)

    @api.model_create_multi
    def create(self, vals_list):
        """Create transaction records.

        Automatically calculates balance_after if not provided.
        """
        for vals in vals_list:
            if 'balance_after' not in vals and 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                current_balance = partner.loyalty_points or 0
                vals['balance_after'] = current_balance + vals.get('points', 0)
        return super().create(vals_list)

    def write(self, vals):
        """Prevent modification of transaction records."""
        # Allow only certain fields to be written (for admin purposes)
        allowed_fields = {'notes'}
        if set(vals.keys()) - allowed_fields:
            raise models.UserError(
                _("Loyalty transactions cannot be modified. "
                  "Only notes can be updated.")
            )
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of transaction records."""
        raise models.UserError(
            _("Loyalty transactions cannot be deleted. "
              "They serve as an audit trail.")
        )
