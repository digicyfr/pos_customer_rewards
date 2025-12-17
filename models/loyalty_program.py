# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LoyaltyProgram(models.Model):
    """Loyalty Program Configuration.

    Stores loyalty program configuration per company.
    Only one active program is allowed per company.
    """
    _name = 'loyalty.program'
    _description = 'Loyalty Program'
    _order = 'name'

    name = fields.Char(
        string="Program Name",
        required=True,
        default="Loyalty Program",
        help="Name of the loyalty program displayed to customers.",
    )
    active = fields.Boolean(
        default=True,
        help="If unchecked, the loyalty program will be hidden and not available.",
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        help="Company this loyalty program belongs to.",
    )

    # Earning Configuration
    points_per_currency = fields.Float(
        string="Points per Currency Unit",
        default=1.0,
        help="Number of points earned per currency unit spent. "
             "For example, 1.0 means 1 point per dollar/euro spent.",
    )
    minimum_order_amount = fields.Float(
        string="Minimum Order Amount",
        default=0.0,
        help="Minimum order amount required to earn points. "
             "Set to 0 for no minimum.",
    )

    # Expiration
    point_expiration_days = fields.Integer(
        string="Points Expire After (days)",
        default=0,
        help="Number of days after which points expire. "
             "Set to 0 for points that never expire.",
    )

    # Display
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        related='company_id.currency_id',
        readonly=True,
    )

    # Related rewards
    reward_ids = fields.One2many(
        comodel_name='loyalty.reward',
        inverse_name='program_id',
        string="Rewards",
    )
    reward_count = fields.Integer(
        string="Reward Count",
        compute='_compute_reward_count',
    )

    _sql_constraints = [
        (
            'company_unique',
            'UNIQUE(company_id)',
            'Only one loyalty program is allowed per company.'
        ),
        (
            'points_positive',
            'CHECK(points_per_currency > 0)',
            'Points per currency must be greater than 0.'
        ),
        (
            'minimum_order_non_negative',
            'CHECK(minimum_order_amount >= 0)',
            'Minimum order amount cannot be negative.'
        ),
        (
            'expiration_non_negative',
            'CHECK(point_expiration_days >= 0)',
            'Point expiration days cannot be negative.'
        ),
    ]

    @api.depends('reward_ids')
    def _compute_reward_count(self):
        """Compute the number of rewards in the program."""
        for program in self:
            program.reward_count = len(program.reward_ids)

    def calculate_points(self, order_amount):
        """Calculate points earned for a given order amount.

        Args:
            order_amount: Total order amount in company currency

        Returns:
            Integer number of points earned (0 if below minimum)
        """
        self.ensure_one()
        if order_amount < self.minimum_order_amount:
            return 0
        return int(order_amount * self.points_per_currency)

    @api.model
    def get_active_program(self, company_id=None):
        """Get the active loyalty program for a company.

        Args:
            company_id: Company ID (defaults to current company)

        Returns:
            loyalty.program record or empty recordset
        """
        if company_id is None:
            company_id = self.env.company.id
        return self.search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], limit=1)

    def action_view_rewards(self):
        """Open the rewards view for this program."""
        self.ensure_one()
        return {
            'name': _('Rewards'),
            'type': 'ir.actions.act_window',
            'res_model': 'loyalty.reward',
            'view_mode': 'tree,form',
            'domain': [('program_id', '=', self.id)],
            'context': {'default_program_id': self.id},
        }
