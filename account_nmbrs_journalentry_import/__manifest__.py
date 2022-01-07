# See LICENSE file for full copyright and licensing details.

{
    "name": "Importeer Nmbrs loonjournaal",
    "version": "15.0.1.0.0",
    "author": "Odoo Experts B.V.",
    "website": "https://www.odooexperts.nl",
    "category": "Accounting",
    "price": 97.00,
    "currency": "EUR",
    "images": [],
    "depends": ["base", "account", "account_accountant", "account_asset"],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_journal_view.xml",
        "view/import_journal_view.xml",
    ],
    "demo_xml": [],
    "test": [],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
}
