# DSL Membership Loyalty

## Overview

DSL Membership Loyalty is a custom Odoo 17 module that extends the Contact Management system to support Membership and Agent management.

The module allows users to classify contacts as Members or Agents and automatically generates Portal Users for them. This module provides a foundation for implementing loyalty programs, membership benefits, agent management, and customer self-service portals.

---

## Features

### Membership Management

* Mark a contact as a Membership Customer.
* Automatically filter membership contacts from the Membership menu.
* Create and manage membership records from a dedicated menu.

### Agent Management

* Mark a contact as an Agent.
* Automatically filter agent contacts from the Agent menu.
* Create and manage agent records from a dedicated menu.

### Portal User Auto Creation

* Automatically creates a Portal User when a Membership or Agent contact is created.
* Uses the contact email as the login credential.
* Links existing users automatically if the email already exists.
* Prevents duplicate portal user creation.
* Maintains a relationship between the contact and portal user.

### Contact Form Customization

* Email field is mandatory.
* Membership and Agent flags added to the contact form.
* Custom Membership and Agent menus.
* Simplified user interface for membership management.

---

## Module Structure

```text
dsl_membership_loyalty/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_partner.py
├── views/
│   ├── menu_items.xml
│   └── res_partner_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

---

## Fields Added

### res.partner

| Field Name     | Type                 | Description                               |
| -------------- | -------------------- | ----------------------------------------- |
| is_membership  | Boolean              | Indicates whether the contact is a member |
| is_agent       | Boolean              | Indicates whether the contact is an agent |
| portal_user_id | Many2one (res.users) | Linked portal user                        |

---

## Menus

### Membership & Loyalty

* Membership
* Agent

---

## Technical Details

### Odoo Version

* Odoo 17 Community / Enterprise

### Dependencies

* base
* contacts
* portal

### Extended Model

```python
res.partner
```

---

## Future Enhancements

* Membership ID Generation
* Agent Code Generation
* Loyalty Point Management
* Membership Types
* Membership Expiry Management
* Loyalty Point Transactions
* Sales Integration
* Membership Discount Rules
* Membership Dashboard
* Reports and Analytics
* Membership Portal
* Agent Portal

---

## License

LGPL-3
