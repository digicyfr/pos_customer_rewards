# POS Customer Rewards - User Guide

A simple loyalty program for your Point of Sale that rewards customers with points and lets them redeem those points for discounts and free products.

---

## What Does This Module Do?

- **Customers earn points** when they make purchases
- **Customers redeem points** for rewards (discounts or free products)
- **Automatic tracking** of all point transactions
- **Easy to use** interface integrated in your POS

---

## Quick Setup (4 Steps)

### Step 1: Create a Loyalty Program

1. Go to: **Point of Sale � Configuration � Loyalty Programs**
2. Click **Create**
3. Fill in:
   - **Program Name**: "Loyalty Program" (or your preferred name)
   - **Points per Currency Unit**: `1.0` (means 1 point per $1 spent)
   - **Minimum Order Amount**: `0` (or set minimum like `10` for $10 minimum)
   - **Points Expire After**: `0` (never expire) or `365` (1 year)
4. Click **Save**

### Step 2: Create Rewards

1. From the Loyalty Program, click **Rewards** button
2. Click **Create**
3. Choose reward type:

**Option A: Fixed Discount**
- Name: "$5 Off"
- Points Required: 100
- Reward Type: Fixed Discount
- Discount Amount: 5.00

**Option B: Percentage Discount**
- Name: "10% Off"
- Points Required: 200
- Reward Type: Percentage Discount
- Discount Percentage: 10

**Option C: Free Product**
- Name: "Free Coffee"
- Points Required: 50
- Reward Type: Free Product
- Free Product: (select a product)

4. Click **Save**

**Tip**: Create 3-4 rewards at different point levels to give customers choices.

### Step 3: Enable in POS

1. Go to: **Point of Sale � Configuration � Point of Sale**
2. Open your POS configuration
3. Enable **Loyalty Program** and select your program
4. Click **Save**

### Step 4: Restart POS

1. Close any open POS sessions
2. Refresh your browser
3. Start a new POS session

 **Done! Your loyalty program is now active.**

---

## How to Use in POS

### For Cashiers: Earning Points

1. **Select customer** at the start of order
2. **Add products** to cart normally
3. **Complete payment** and validate order
4. **Points are automatically added** to customer's account

### For Cashiers: Redeeming Points

1. **Select customer** and add products to cart
2. **Click "Use Points" button** (on the product screen)
3. **Select a reward** from the popup
4. **Click "Redeem"**
5. Discount is applied to the order
6. **Complete payment** for remaining amount
7. **Validate order**

**Important**:
- Customer must be selected BEFORE clicking "Use Points"
- Only ONE reward can be redeemed per order
- Rewards show current point balance

---

## Workflow Example

**Scenario**: Customer spends $50 and later redeems points

### Visit 1: Customer Earns Points
```
Customer spends: $50
Points earned: 50 points (1 point per $1)
Customer balance: 50 points
```

### Visit 2: Customer Spends More
```
Customer spends: $75
Points earned: 75 points
Customer balance: 125 points
```

### Visit 3: Customer Redeems Points
```
Customer balance: 125 points
Customer selects: "$5 Off" reward (costs 100 points)

Order total: $30
Discount applied: -$5
New total: $25

After payment:
- Points deducted: 100
- Remaining points: 25
```

---

## Common Questions

### Can customers redeem multiple rewards in one order?
No, only one reward per order.

### What happens if customer doesn't have enough points?
Rewards requiring more points will appear grayed out in the popup.

### Can I change the earning rate later?
Yes, but it only affects NEW orders, not existing points.

### Do I need to create a discount product manually?
No, the module automatically creates and manages the "Loyalty Discount" product.

### Can I manually adjust customer points?
Yes, administrators can manually add/remove points from the customer's record.

### How do I see a customer's point balance?
- In POS: Points show when you select the customer
- In Backend: Open customer record, view "Loyalty Points" field

### Where can I see transaction history?
Go to: **Point of Sale � Reporting � Loyalty Transactions**

---


## Tips for Success

### For Business Owners
1. **Start simple**: Begin with 2-3 rewards
2. **Make it attractive**: Rewards should feel valuable to customers
3. **Train your staff**: Ensure cashiers know how to use the system
4. **Promote it**: Tell customers about your loyalty program
5. **Monitor usage**: Check what rewards are popular

### For Cashiers
1. **Always ask**: "Are you a loyalty member?"
2. **Remind customers**: Tell them how many points they have
3. **Suggest rewards**: "You have enough points for $5 off!"
4. **Be patient**: First-time users may need extra help

### Recommended Reward Structure
```
50 points   � $2 off or Small free item
100 points  � $5 off
200 points  � $10 off or 10% discount
500 points  � $25 off or Premium item
```

---

## Module Information

- **Version**: 17.0.1.2.0
- **License**: LGPL-3
- **Compatible with**: Odoo 17.0 Community & Enterprise
- **Dependencies**: Point of Sale

---

## Support

For issues or questions:
1. Check this documentation
2. Enable Developer Mode for technical details
3. Contact Digicyfr Polska support:
   - **Website**: https://digicyfr.com
   - **Email**: info@digicyfr.com
   - **Phone**: +48 695 021 633
4. Check module logs: `/var/log/odoo/odoo-server.log`

---

**Thank you for using POS Customer Rewards!**

Developed by **Digicyfr Polska** | https://digicyfr.com
