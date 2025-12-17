# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LoyaltyReward(models.Model):
    """Loyalty Reward Configuration.

    Defines rewards that customers can redeem using their loyalty points.
    """
    _name = 'loyalty.reward'
    _description = 'Loyalty Reward'
    _order = 'points_required, name'

    name = fields.Char(
        string="Reward Name",
        required=True,
        help="Name of the reward displayed to customers.",
    )
    program_id = fields.Many2one(
        comodel_name='loyalty.program',
        string="Loyalty Program",
        required=True,
        ondelete='cascade',
        help="The loyalty program this reward belongs to.",
    )
    active = fields.Boolean(
        default=True,
        help="If unchecked, the reward will be hidden and not available for redemption.",
    )

    # Redemption Cost
    points_required = fields.Integer(
        string="Points Required",
        required=True,
        help="Number of points required to redeem this reward.",
    )

    # Reward Type
    reward_type = fields.Selection(
        selection=[
            ('discount_fixed', 'Fixed Discount'),
            ('discount_percent', 'Percentage Discount'),
            ('free_product', 'Free Product'),
        ],
        string="Reward Type",
        required=True,
        default='discount_fixed',
        help="Type of discount applied when redeeming this reward.",
    )

    discount_amount = fields.Float(
        string="Discount Amount",
        help="Fixed discount amount applied to the order.",
    )
    discount_percentage = fields.Float(
        string="Discount Percentage (%)",
        help="Percentage discount applied to the order (0-100).",
    )

    # Free Product fields
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Free Product",
        domain="[('available_in_pos', '=', True)]",
        ondelete='restrict',
        help="Product given for free when redeeming this reward. "
             "Only products available in POS can be selected.",
    )
    product_list_price = fields.Float(
        string="Product Value",
        related='product_id.lst_price',
        readonly=True,
        help="Value of the free product.",
    )

    # Display
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        related='program_id.company_id',
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        related='company_id.currency_id',
        readonly=True,
    )

    _sql_constraints = [
        (
            'points_positive',
            'CHECK(points_required > 0)',
            'Points required must be greater than 0.'
        ),
        (
            'discount_amount_non_negative',
            'CHECK(discount_amount >= 0)',
            'Discount amount cannot be negative.'
        ),
        (
            'discount_percentage_range',
            'CHECK(discount_percentage >= 0 AND discount_percentage <= 100)',
            'Discount percentage must be between 0 and 100.'
        ),
    ]

    @api.constrains('reward_type', 'discount_amount', 'discount_percentage', 'product_id')
    def _check_discount_values(self):
        """Ensure discount values are set correctly based on reward type."""
        for reward in self:
            if reward.reward_type == 'discount_fixed' and not reward.discount_amount:
                raise ValidationError(
                    _("Discount amount is required for fixed discount rewards.")
                )
            if reward.reward_type == 'discount_percent' and not reward.discount_percentage:
                raise ValidationError(
                    _("Discount percentage is required for percentage discount rewards.")
                )
            if reward.reward_type == 'free_product' and not reward.product_id:
                raise ValidationError(
                    _("Product is required for free product rewards.")
                )

    def get_discount_value(self, order_total=0):
        """Calculate the discount value for this reward.

        Args:
            order_total: Total order amount (used for percentage discounts)

        Returns:
            Float discount amount to apply
        """
        self.ensure_one()
        if self.reward_type == 'discount_fixed':
            return self.discount_amount
        elif self.reward_type == 'discount_percent':
            return order_total * (self.discount_percentage / 100)
        elif self.reward_type == 'free_product':
            return self.product_id.lst_price if self.product_id else 0.0
        return 0.0

    def name_get(self):
        """Custom name display showing points required."""
        result = []
        for reward in self:
            name = f"{reward.name} ({reward.points_required} pts)"
            result.append((reward.id, name))
        return result
