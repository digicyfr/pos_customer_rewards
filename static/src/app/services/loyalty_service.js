/** @odoo-module */

import { registry } from "@web/core/registry";

/**
 * Loyalty Service
 *
 * Central service for loyalty program logic in POS
 */
export const loyaltyService = {
    dependencies: ["pos"],

    start(env) {
        const pos = env.services.pos;

        return {
            /**
             * Check if loyalty is enabled for current POS
             * @returns {boolean}
             */
            isEnabled() {
                return Boolean(pos.loyalty_program);
            },

            /**
             * Calculate points earned for an order amount
             * @param {number} orderAmount - Total order amount
             * @returns {number} Points earned
             */
            calculatePoints(orderAmount) {
                const program = pos.loyalty_program;
                if (!program || orderAmount < program.minimum_order_amount) {
                    return 0;
                }

                return Math.floor(orderAmount * program.points_per_currency);
            },

            /**
             * Get customer's current points balance
             * @param {number} partnerId - Customer ID
             * @returns {number} Points balance
             */
            getCustomerPoints(partnerId) {
                if (!partnerId) {
                    return 0;
                }

                const partner = pos.db.get_partner_by_id(partnerId);
                return partner ? (partner.loyalty_points || 0) : 0;
            },

            /**
             * Get rewards available for redemption
             * @param {number} points - Customer's current points
             * @returns {Array} Available rewards
             */
            getAvailableRewards(points) {
                if (!pos.loyalty_rewards || !points) {
                    return [];
                }

                // Backend already filters for active rewards
                return pos.loyalty_rewards.filter(
                    reward => reward.points_required <= points
                ).sort((a, b) => a.points_required - b.points_required);
            },

            /**
             * Calculate discount value for a reward
             * @param {Object} reward - Reward object
             * @param {number} orderTotal - Current order total
             * @returns {Object} Reward information {type, amount, product, quantity}
             */
            calculateDiscount(reward, orderTotal = 0) {
                if (!reward) {
                    return { type: 'none', amount: 0 };
                }

                if (reward.reward_type === 'discount_fixed') {
                    return {
                        type: 'discount',
                        amount: reward.discount_amount,
                    };
                } else if (reward.reward_type === 'discount_percent') {
                    return {
                        type: 'discount',
                        amount: orderTotal * (reward.discount_percentage / 100),
                    };
                } else if (reward.reward_type === 'free_product') {
                    const productId = Array.isArray(reward.product_id)
                        ? reward.product_id[0]
                        : reward.product_id;
                    const product = pos.db.get_product_by_id(productId);

                    if (!product) {
                        console.error('[Loyalty] Free product not found:', productId);
                        return { type: 'none', amount: 0 };
                    }

                    return {
                        type: 'product',
                        product: product,
                        quantity: 1,
                        amount: product.lst_price,
                    };
                }

                return { type: 'none', amount: 0 };
            },

            /**
             * Get display information for a reward
             * @param {Object} reward - Reward object
             * @returns {Object} Display info {text, description}
             */
            getRewardDisplayInfo(reward) {
                if (!reward) {
                    return { text: '', description: '' };
                }

                const currencySymbol = pos.currency.symbol || '$';

                if (reward.reward_type === 'discount_fixed') {
                    return {
                        text: `${currencySymbol}${reward.discount_amount.toFixed(2)} off`,
                        description: `Save ${currencySymbol}${reward.discount_amount.toFixed(2)}`,
                    };
                } else if (reward.reward_type === 'discount_percent') {
                    return {
                        text: `${reward.discount_percentage}% off`,
                        description: `Save ${reward.discount_percentage}%`,
                    };
                } else if (reward.reward_type === 'free_product') {
                    const productName = Array.isArray(reward.product_id)
                        ? reward.product_id[1]
                        : 'Product';
                    const productId = Array.isArray(reward.product_id)
                        ? reward.product_id[0]
                        : reward.product_id;
                    const product = pos.db.get_product_by_id(productId);
                    const value = product ? product.lst_price : 0;

                    return {
                        text: `Free ${productName}`,
                        description: `Free ${productName} (worth ${currencySymbol}${value.toFixed(2)})`,
                    };
                }

                return { text: '', description: '' };
            },
        };
    },
};

registry.category("services").add("loyalty", loyaltyService);
