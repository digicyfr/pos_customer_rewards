/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { LoyaltyPopup } from "../../popups/loyalty_popup";

export class UsePointsButton extends Component {
    static template = "pos_customer_rewards.UsePointsButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.notification = useService("notification");
    }

    /**
     * Handle Use Points button click
     */
    async onClick() {
        const order = this.pos.get_order();
        const partner = order?.get_partner();

        if (!partner) {
            this.notification.add(_t("Please select a customer first."));
            return;
        }

        if (!this.env.services.loyalty) {
            this.notification.add(_t("Loyalty service is not available."));
            return;
        }

        const loyaltyService = this.env.services.loyalty;

        if (!loyaltyService.isEnabled()) {
            this.notification.add(_t("Loyalty program is not configured for this POS."));
            return;
        }

        const points = loyaltyService.getCustomerPoints(partner.id);
        const rewards = loyaltyService.getAvailableRewards(points);

        if (points === 0) {
            this.notification.add(_t("Customer has no loyalty points."));
            return;
        }

        if (rewards.length === 0) {
            this.notification.add(_t("No rewards available with current points."));
            return;
        }

        // Show loyalty popup
        const { confirmed, payload } = await this.popup.add(LoyaltyPopup, {
            title: _t("Redeem Loyalty Points"),
            customerPoints: points,
            rewards: rewards,
        });

        if (confirmed && payload && payload.reward) {
            // Apply reward to order
            try {
                const success = await order.applyLoyaltyReward(payload.reward);

                if (success) {
                    this.notification.add(_t("Loyalty reward applied successfully!"));
                } else {
                    this.notification.add(_t("Failed to apply loyalty reward."));
                }
            } catch (error) {
                console.error('[Loyalty] Error applying reward:', error);
                this.notification.add(_t("Error applying reward: ") + error.message);
            }
        }
    }
}

// Replace the Customer Note button position with Use Points button
ProductScreen.addControlButton({
    component: UsePointsButton,
    position: ['replace', 'OrderlineCustomerNoteButton'],
});
