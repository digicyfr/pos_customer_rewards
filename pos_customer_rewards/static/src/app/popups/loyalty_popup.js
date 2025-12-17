/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

/**
 * Loyalty Popup - Reward Selection
 */
export class LoyaltyPopup extends AbstractAwaitablePopup {
    static template = "pos_customer_rewards.LoyaltyPopup";
    static defaultProps = {
        confirmText: _t("Redeem"),
        cancelText: _t("Cancel"),
        title: _t("Redeem Loyalty Points"),
        customerPoints: 0,
        rewards: [],
    };

    setup() {
        super.setup();
        this.state = useState({
            selectedReward: null,
        });
        this.title = this.props.title;
        this.customerPoints = this.props.customerPoints;
        this.rewards = this.props.rewards;
    }

    /**
     * Select a reward
     */
    selectReward = (reward) => {
        this.state.selectedReward = reward;
    }

    /**
     * Confirm reward selection
     */
    confirm = async () => {
        if (!this.state.selectedReward) {
            this.env.services.notification.add(
                _t("Please select a reward first.")
            );
            return;
        }

        this.props.resolve({ confirmed: true, payload: { reward: this.state.selectedReward } });
        super.confirm();
    }

    /**
     * Cancel and close popup
     */
    cancel = () => {
        this.props.resolve({ confirmed: false, payload: null });
        super.cancel();
    }

    /**
     * Get reward display info
     */
    getRewardInfo = (reward) => {
        let discountText = "";
        if (reward.reward_type === 'discount_fixed') {
            discountText = this.env.utils.formatCurrency(reward.discount_amount);
        } else if (reward.reward_type === 'discount_percent') {
            discountText = `${reward.discount_percentage}%`;
        }

        return {
            name: reward.name,
            points: reward.points_required,
            discount: discountText,
        };
    }

    /**
     * Get reward description for display
     */
    getRewardDescription = (reward) => {
        const loyaltyService = this.env.services.loyalty;
        const info = loyaltyService.getRewardDisplayInfo(reward);
        return info.description;
    }

    /**
     * Check if reward is selected
     */
    isSelected = (reward) => {
        return this.state.selectedReward && this.state.selectedReward.id === reward.id;
    }
}
