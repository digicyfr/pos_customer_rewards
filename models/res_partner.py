# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from odoo import api, fields, models, _


class ResPartner(models.Model):
    """Extend res.partner with loyalty points functionality."""
    _inherit = 'res.partner'

    loyalty_points = fields.Integer(
        string="Loyalty Points",
        compute='_compute_loyalty_points',
        store=True,
        help="Current loyalty points balance for this customer.",
    )
    loyalty_transaction_ids = fields.One2many(
        comodel_name='loyalty.transaction',
        inverse_name='partner_id',
        string="Loyalty Transactions",
        help="History of loyalty point transactions.",
    )
    loyalty_transaction_count = fields.Integer(
        string="Transaction Count",
        compute='_compute_loyalty_transaction_count',
    )

    @api.depends('loyalty_transaction_ids.points')
    def _compute_loyalty_points(self):
        """Calculate current points balance from transactions.

        Considers expiration if configured in the loyalty program.
        """
        for partner in self:
            total_points = sum(partner.loyalty_transaction_ids.mapped('points'))
            partner.loyalty_points = max(0, total_points)

    @api.depends('loyalty_transaction_ids')
    def _compute_loyalty_transaction_count(self):
        """Compute the number of loyalty transactions."""
        for partner in self:
            partner.loyalty_transaction_count = len(partner.loyalty_transaction_ids)

    def add_loyalty_points(self, points, program, pos_order=None, notes=None):
        """Add points to customer's loyalty balance.

        Args:
            points: Number of points to add (positive integer)
            program: loyalty.program record
            pos_order: Optional pos.order record
            notes: Optional notes for the transaction

        Returns:
            Created loyalty.transaction record
        """
        self.ensure_one()
        if points <= 0:
            return self.env['loyalty.transaction']

        transaction = self.env['loyalty.transaction'].create({
            'partner_id': self.id,
            'program_id': program.id,
            'transaction_type': 'earn',
            'points': points,
            'pos_order_id': pos_order.id if pos_order else False,
            'notes': notes,
        })
        return transaction

    def redeem_points(self, points, program, reward=None, pos_order=None, notes=None):
        """Redeem points from customer's loyalty balance.

        Args:
            points: Number of points to redeem (positive integer)
            program: loyalty.program record
            reward: Optional loyalty.reward record
            pos_order: Optional pos.order record
            notes: Optional notes for the transaction

        Returns:
            Created loyalty.transaction record

        Raises:
            UserError: If insufficient points
        """
        self.ensure_one()
        if points <= 0:
            return self.env['loyalty.transaction']

        if self.loyalty_points < points:
            raise models.UserError(
                _("Insufficient loyalty points. Customer has %(current)d points, "
                  "but %(required)d are required.",
                  current=self.loyalty_points,
                  required=points)
            )

        transaction = self.env['loyalty.transaction'].create({
            'partner_id': self.id,
            'program_id': program.id,
            'transaction_type': 'redeem',
            'points': -points,  # Negative for redemption
            'reward_id': reward.id if reward else False,
            'pos_order_id': pos_order.id if pos_order else False,
            'notes': notes,
        })
        return transaction

    def expire_old_points(self, program):
        """Expire points older than the program's expiration period.

        Args:
            program: loyalty.program record with point_expiration_days set

        Returns:
            Created loyalty.transaction record for expiration (or empty recordset)
        """
        self.ensure_one()
        if not program.point_expiration_days:
            return self.env['loyalty.transaction']

        expiration_date = fields.Datetime.now() - timedelta(days=program.point_expiration_days)

        # Find transactions that should expire (earn transactions older than expiration date)
        # that haven't been fully consumed by redemptions
        old_earn_transactions = self.env['loyalty.transaction'].search([
            ('partner_id', '=', self.id),
            ('program_id', '=', program.id),
            ('transaction_type', '=', 'earn'),
            ('date', '<', expiration_date),
        ])

        if not old_earn_transactions:
            return self.env['loyalty.transaction']

        # Calculate points to expire
        # This is a simplified approach - in production you might want
        # to track individual point batches and their expiration
        old_earned = sum(old_earn_transactions.mapped('points'))

        # Get all redemptions and expirations
        consumed_transactions = self.env['loyalty.transaction'].search([
            ('partner_id', '=', self.id),
            ('program_id', '=', program.id),
            ('transaction_type', 'in', ['redeem', 'expire']),
        ])
        total_consumed = abs(sum(consumed_transactions.mapped('points')))

        # Points that can expire = old earned - already consumed
        points_to_expire = max(0, old_earned - total_consumed)

        if points_to_expire <= 0:
            return self.env['loyalty.transaction']

        # Create expiration transaction
        transaction = self.env['loyalty.transaction'].create({
            'partner_id': self.id,
            'program_id': program.id,
            'transaction_type': 'expire',
            'points': -points_to_expire,
            'notes': _("Points expired after %(days)d days", days=program.point_expiration_days),
        })
        return transaction

    def action_view_loyalty_transactions(self):
        """Open the loyalty transactions view for this partner."""
        self.ensure_one()
        return {
            'name': _('Loyalty Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'loyalty.transaction',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def get_available_rewards(self, program):
        """Get rewards available for redemption based on current points.

        Args:
            program: loyalty.program record

        Returns:
            loyalty.reward recordset of available rewards
        """
        self.ensure_one()
        return self.env['loyalty.reward'].search([
            ('program_id', '=', program.id),
            ('active', '=', True),
            ('points_required', '<=', self.loyalty_points),
        ])
