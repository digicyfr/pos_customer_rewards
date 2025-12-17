/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { OrderlineCustomerNoteButton } from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";

// Re-add the Customer Note button after the Use Points button
ProductScreen.addControlButton({
    component: OrderlineCustomerNoteButton,
    position: ['after', 'UsePointsButton'],
});
