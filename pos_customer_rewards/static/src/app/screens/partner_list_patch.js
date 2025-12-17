/** @odoo-module */

import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

/**
 * Patch PartnerLine to show loyalty points
 */
patch(PartnerLine.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    /**
     * Get customer's loyalty points for display
     */
    get loyaltyPoints() {
        if (!this.props.partner || !this.env.services.loyalty) {
            return null;
        }

        const loyaltyService = this.env.services.loyalty;

        if (!loyaltyService.isEnabled()) {
            return null;
        }

        return loyaltyService.getCustomerPoints(this.props.partner.id);
    },

    /**
     * Check if customer has redeemable points
     */
    get hasRedeemablePoints() {
        const points = this.loyaltyPoints;
        if (!points) {
            return false;
        }

        const loyaltyService = this.env.services.loyalty;
        const rewards = loyaltyService.getAvailableRewards(points);

        return rewards.length > 0;
    },
});
