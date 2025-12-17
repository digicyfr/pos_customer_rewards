# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Extend pos.config to enable loyalty program per POS."""
    _inherit = 'pos.config'

    loyalty_program_id = fields.Many2one(
        comodel_name='loyalty.program',
        string="Loyalty Program",
        domain="[('company_id', '=', company_id), ('active', '=', True)]",
        help="Select a loyalty program for this POS. "
             "Customers will earn and redeem points when enabled.",
    )
    loyalty_enabled = fields.Boolean(
        string="Loyalty Enabled",
        compute='_compute_loyalty_enabled',
        help="Whether loyalty is enabled for this POS.",
    )

    @api.depends('loyalty_program_id', 'loyalty_program_id.active')
    def _compute_loyalty_enabled(self):
        """Compute if loyalty is enabled for this POS."""
        for config in self:
            config.loyalty_enabled = bool(
                config.loyalty_program_id and config.loyalty_program_id.active
            )

    def _get_loyalty_discount_product(self):
        """Get the loyalty discount product by XML ID.

        Returns:
            product.product record or empty recordset
        """
        return self.env.ref(
            'pos_customer_rewards.product_loyalty_discount',
            raise_if_not_found=False
        )


class PosSession(models.Model):
    """Extend pos.session to load loyalty data."""
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        """Add loyalty models to POS data loading."""
        result = super()._pos_ui_models_to_load()
        result.extend(['loyalty.program', 'loyalty.reward'])
        return result

    def _loader_params_loyalty_program(self):
        """Parameters for loading loyalty programs."""
        return {
            'search_params': {
                'domain': [
                    ('id', '=', self.config_id.loyalty_program_id.id),
                    ('active', '=', True),
                ],
                'fields': [
                    'name',
                    'points_per_currency',
                    'minimum_order_amount',
                    'point_expiration_days',
                ],
            },
        }

    def _get_pos_ui_loyalty_program(self, params):
        """Load loyalty program for POS."""
        return self.env['loyalty.program'].search_read(**params['search_params'])

    def _loader_params_loyalty_reward(self):
        """Parameters for loading loyalty rewards."""
        program_id = self.config_id.loyalty_program_id.id
        return {
            'search_params': {
                'domain': [
                    ('program_id', '=', program_id),
                    ('active', '=', True),
                ],
                'fields': [
                    'name',
                    'program_id',
                    'points_required',
                    'reward_type',
                    'discount_amount',
                    'discount_percentage',
                    'product_id',
                ],
            },
        }

    def _get_pos_ui_loyalty_reward(self, params):
        """Load loyalty rewards for POS."""
        return self.env['loyalty.reward'].search_read(**params['search_params'])

    def _get_pos_ui_res_partner(self, params):
        """Override to inject loyalty_points from database."""
        # Call parent to load normal partner data
        partners = super()._get_pos_ui_res_partner(params)

        # Manually inject loyalty_points from database for each partner
        if partners:
            partner_ids = [p['id'] for p in partners]

            # Direct SQL query to get loyalty_points since ORM doesn't recognize the field
            self.env.cr.execute("""
                SELECT id, COALESCE(loyalty_points, 0) as loyalty_points
                FROM res_partner
                WHERE id IN %s
            """, (tuple(partner_ids),))

            loyalty_data = {row[0]: row[1] for row in self.env.cr.fetchall()}

            # Inject loyalty_points into each partner record
            for partner in partners:
                partner['loyalty_points'] = loyalty_data.get(partner['id'], 0)

        return partners

    def _pos_data_process(self, loaded_data):
        """Process loaded POS data including loyalty."""
        super()._pos_data_process(loaded_data)

        # Make loyalty data easily accessible
        if loaded_data.get('loyalty.program'):
            loaded_data['loyalty_program'] = loaded_data['loyalty.program'][0] if loaded_data['loyalty.program'] else None
        else:
            loaded_data['loyalty_program'] = None

        loaded_data['loyalty_rewards'] = loaded_data.get('loyalty.reward', [])

        # Add auto-resolved discount product ID
        discount_product = self.config_id._get_loyalty_discount_product()
        loaded_data['loyalty_discount_product_id'] = discount_product.id if discount_product else None

        # Ensure discount product is loaded in POS
        if discount_product and 'product.product' in loaded_data:
            product_ids = [p['id'] for p in loaded_data['product.product']]

            if discount_product.id not in product_ids:
                # Get an existing product to copy field structure
                if loaded_data['product.product']:
                    sample = loaded_data['product.product'][0]
                    # Create discount product data matching the same structure
                    discount_product_data = {}
                    for key in sample.keys():
                        try:
                            # Get the field value from the discount product
                            if hasattr(discount_product, key):
                                value = getattr(discount_product, key, False)
                                # Handle Many2one fields (they're tuples in search_read)
                                if hasattr(value, 'id'):
                                    discount_product_data[key] = [value.id, value.display_name] if hasattr(value, 'display_name') else value.id
                                # Handle Many2many fields
                                elif hasattr(value, 'ids'):
                                    discount_product_data[key] = value.ids
                                else:
                                    discount_product_data[key] = value
                            else:
                                discount_product_data[key] = False
                        except Exception as e:
                            _logger.error(f"Error reading field {key} from loyalty discount product: {e}")
                            discount_product_data[key] = False

                    loaded_data['product.product'].append(discount_product_data)
                else:
                    _logger.error("Cannot load loyalty discount product: no sample product available")

            if not discount_product:
                _logger.error("Loyalty discount product XML ID not found")
