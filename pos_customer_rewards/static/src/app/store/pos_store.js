/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

/**
 * Patch PosStore to load loyalty data
 */
patch(PosStore.prototype, {
    /**
     * Process loaded POS data including loyalty
     */
    async _processData(loadedData) {
        await super._processData(...arguments);

        // Store loyalty program
        this.loyalty_program = loadedData.loyalty_program || null;

        // Store loyalty rewards
        this.loyalty_rewards = loadedData.loyalty_rewards || [];

        // Store discount product ID (auto-resolved from XML ID)
        this.loyalty_discount_product_id = loadedData.loyalty_discount_product_id || null;

        console.log('[Loyalty] Data loaded:', {
            program: this.loyalty_program,
            rewards: this.loyalty_rewards,
            discountProductId: this.loyalty_discount_product_id
        });
    },
});
