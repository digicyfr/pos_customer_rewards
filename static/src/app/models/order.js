/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.loyalty_points_earned = this.loyalty_points_earned || 0;
        this.loyalty_points_redeemed = this.loyalty_points_redeemed || 0;
        this.loyalty_reward_id = this.loyalty_reward_id || null;
        this.loyalty_discount = this.loyalty_discount || 0;
    },

    applyLoyaltyReward(reward) {
        const loyaltyService = this.pos.env.services.loyalty;
        const rewardInfo = loyaltyService.calculateDiscount(reward, this.get_total_with_tax());

        // Get discount product ID from loaded data
        const discountProductId = this.pos.loyalty_discount_product_id;

        if (!discountProductId) {
            console.error("Loyalty discount product not found.");
            this.env.services.notification.add(
                "Loyalty discount product is not available. Please contact administrator."
            );
            return false;
        }

        const discountProduct = this.pos.db.get_product_by_id(discountProductId);

        if (!discountProduct) {
            console.error("Loyalty discount product ID", discountProductId, "not loaded in POS");
            this.env.services.notification.add(
                "Loyalty discount product is not available in POS. Please contact administrator."
            );
            return false;
        }

        // Remove existing loyalty discount lines
        const existingDiscounts = this.orderlines.filter(
            line => line.product.id === discountProduct.id
        );
        existingDiscounts.forEach(line => this.remove_orderline(line));

        // Store reward metadata
        this.loyalty_reward_id = reward.id;
        this.loyalty_points_redeemed = reward.points_required;

        // Handle different reward types
        if (rewardInfo.type === 'product') {
            // Validate product exists
            if (!rewardInfo.product) {
                this.env.services.notification.add(
                    "Product for this reward is not available in POS."
                );
                return false;
            }

            // Add product at original price
            this.add_product(rewardInfo.product, {
                quantity: rewardInfo.quantity,
                merge: false,
            });

            // Add discount line for product price
            this.add_product(discountProduct, {
                price: -rewardInfo.amount,
                quantity: 1,
                merge: false,
            });

            this.loyalty_discount = rewardInfo.amount;

        } else if (rewardInfo.type === 'discount') {
            // Standard discount application
            this.add_product(discountProduct, {
                price: -rewardInfo.amount,
                quantity: 1,
                merge: false,
            });

            this.loyalty_discount = rewardInfo.amount;

        } else {
            console.error('Unknown reward type:', rewardInfo.type);
            return false;
        }

        return true;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.loyalty_points_earned = this.loyalty_points_earned;
        json.loyalty_points_redeemed = this.loyalty_points_redeemed;
        json.loyalty_reward_id = this.loyalty_reward_id;
        json.loyalty_discount = this.loyalty_discount;
        return json;
    },
});
