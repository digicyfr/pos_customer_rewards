# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class PosOrder(models.Model):
    """Extend pos.order with loyalty points tracking."""
    _inherit = 'pos.order'

    loyalty_points_earned = fields.Integer(
        string="Loyalty Points Earned",
        readonly=True,
        help="Number of loyalty points earned from this order.",
    )
    loyalty_points_redeemed = fields.Integer(
        string="Loyalty Points Redeemed",
        readonly=True,
        help="Number of loyalty points redeemed in this order.",
    )
    loyalty_reward_id = fields.Many2one(
        comodel_name='loyalty.reward',
        string="Loyalty Reward",
        readonly=True,
        ondelete='set null',
        help="Loyalty reward that was redeemed in this order.",
    )
    loyalty_discount = fields.Float(
        string="Loyalty Discount",
        readonly=True,
        help="Discount amount applied from loyalty redemption.",
    )
    loyalty_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Loyalty Product",
        readonly=True,
        ondelete='set null',
        help="Free product received through loyalty redemption.",
    )

    @api.model
    def _order_fields(self, ui_order):
        """Extract loyalty fields from POS UI order data."""
        fields = super()._order_fields(ui_order)

        # Extract loyalty data from UI order
        fields['loyalty_points_earned'] = ui_order.get('loyalty_points_earned', 0)
        fields['loyalty_points_redeemed'] = ui_order.get('loyalty_points_redeemed', 0)
        fields['loyalty_reward_id'] = ui_order.get('loyalty_reward_id', False)
        fields['loyalty_discount'] = ui_order.get('loyalty_discount', 0.0)

        return fields

    def _process_order(self, order, draft, existing_order):
        """Process loyalty points after order validation."""
        order_id = super()._process_order(order, draft, existing_order)

        if order_id:
            pos_order = self.browse(order_id)
            pos_order._process_loyalty_points()

        return order_id

    def _process_loyalty_points(self):
        """Process loyalty earning/redemption after order validation.

        This method is called after the order is created to:
        1. Award points for the purchase (if eligible)
        2. Record redemption transaction (if points were used)
        """
        self.ensure_one()

        # Skip if no customer
        if not self.partner_id:
            return

        # Get loyalty program from POS config
        program = self.config_id.loyalty_program_id
        if not program or not program.active:
            return

        # Check if transaction already exists for this order to avoid duplicates
        existing_transaction = self.env['loyalty.transaction'].search([
            ('pos_order_id', '=', self.id)
        ], limit=1)
        if existing_transaction:
            return  # Already processed

        # Calculate points if not already set (when POS UI is disabled)
        if self.loyalty_points_earned == 0 and self.amount_total > 0:
            points_to_earn = program.calculate_points(self.amount_total)
            if points_to_earn > 0:
                self.write({'loyalty_points_earned': points_to_earn})

        # Process points earning
        if self.loyalty_points_earned > 0:
            self.partner_id.add_loyalty_points(
                points=self.loyalty_points_earned,
                program=program,
                pos_order=self,
                notes=_("Points earned from POS order"),
            )

        # Process points redemption
        if self.loyalty_points_redeemed > 0:
            self.partner_id.redeem_points(
                points=self.loyalty_points_redeemed,
                program=program,
                reward=self.loyalty_reward_id,
                pos_order=self,
                notes=_("Points redeemed in POS order"),
            )

    def action_view_loyalty_transactions(self):
        """View loyalty transactions related to this order."""
        self.ensure_one()
        return {
            'name': _('Loyalty Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'loyalty.transaction',
            'view_mode': 'tree,form',
            'domain': [('pos_order_id', '=', self.id)],
        }
