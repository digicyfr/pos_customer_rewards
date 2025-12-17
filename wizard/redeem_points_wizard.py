# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RedeemPointsWizard(models.TransientModel):
    """Wizard for redeeming loyalty points."""
    _name = 'redeem.points.wizard'
    _description = 'Redeem Loyalty Points'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        readonly=True,
    )
    current_points = fields.Integer(
        string='Current Points',
        related='partner_id.loyalty_points',
        readonly=True,
    )
    program_id = fields.Many2one(
        comodel_name='loyalty.program',
        string='Loyalty Program',
        required=True,
    )
    reward_id = fields.Many2one(
        comodel_name='loyalty.reward',
        string='Reward',
        required=True,
        domain="[('program_id', '=', program_id), ('active', '=', True)]",
    )
    points_required = fields.Integer(
        string='Points Required',
        related='reward_id.points_required',
        readonly=True,
    )
    discount_amount = fields.Float(
        string='Discount Value',
        compute='_compute_discount_amount',
        readonly=True,
    )
    notes = fields.Text(
        string='Notes',
        default='Manual points redemption',
    )

    @api.depends('reward_id')
    def _compute_discount_amount(self):
        """Compute the discount amount for the selected reward."""
        for wizard in self:
            if wizard.reward_id:
                wizard.discount_amount = wizard.reward_id.get_discount_value()
            else:
                wizard.discount_amount = 0.0

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Set default program when partner changes."""
        if self.partner_id:
            # Try to find an active program
            program = self.env['loyalty.program'].search([('active', '=', True)], limit=1)
            if program:
                self.program_id = program

    def action_redeem(self):
        """Redeem points for the selected reward."""
        self.ensure_one()

        # Validate points
        if self.current_points < self.points_required:
            raise UserError(
                _("Insufficient points! Customer has %(current)d points but needs %(required)d points.",
                  current=self.current_points,
                  required=self.points_required)
            )

        # Redeem the points
        self.partner_id.redeem_points(
            points=self.points_required,
            program=self.program_id,
            reward=self.reward_id,
            notes=self.notes,
        )

        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%(points)d points redeemed for %(reward)s',
                           points=self.points_required,
                           reward=self.reward_id.name),
                'type': 'success',
                'sticky': False,
            }
        }
