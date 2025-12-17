/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { LoyaltyPopup } from "../popups/loyalty_popup";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch PaymentScreen to add "Use Points" button
 */
patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.notification = useService("pos_notification");
        this.popup = useService("popup");
    },

    /**
     * Check if Use Points button should be visible
     */
    get loyaltyButtonVisible() {
        const order = this.currentOrder;
        const partner = order?.get_partner();

        if (!partner || !this.pos.loyalty_program) {
            return false;
        }

        const loyaltyService = this.env.services.loyalty;
        const points = loyaltyService.getCustomerPoints(partner.id);

        // Show button if customer has points and rewards are available
        return points > 0 && loyaltyService.getAvailableRewards(points).length > 0;
    },

    /**
     * Handle Use Points button click
     */
    async clickLoyaltyButton() {
        const order = this.currentOrder;
        const partner = order.get_partner();

        if (!partner) {
            this.env.services.notification.add(
                _t("Please select a customer first."),
                { type: "warning" }
            );
            return;
        }

        const loyaltyService = this.env.services.loyalty;
        const points = loyaltyService.getCustomerPoints(partner.id);
        const rewards = loyaltyService.getAvailableRewards(points);

        if (rewards.length === 0) {
            this.env.services.notification.add(
                _t("No rewards available with current points."),
                { type: "info" }
            );
            return;
        }

        // Show loyalty popup
        const { confirmed, payload } = await this.env.services.popup.add(LoyaltyPopup, {
            title: _t("Redeem Loyalty Points"),
            customerPoints: points,
            rewards: rewards,
        });

        if (confirmed && payload.reward) {
            // Apply reward to order
            const success = order.applyLoyaltyReward(payload.reward);

            if (success) {
                this.env.services.notification.add(
                    _t("Loyalty reward applied successfully!"),
                    { type: "success" }
                );
            } else {
                this.env.services.notification.add(
                    _t("Failed to apply loyalty reward."),
                    { type: "danger" }
                );
            }
        }
    },
});
