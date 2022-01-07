# See LICENSE file for full copyright and licensing details.

import base64
import os

from odoo import fields
from odoo.tests.common import TransactionCase


class TestImportJournal(TransactionCase):
    # 22635 :  Migratie to V15
    def setUp(self):
        """test setup for import journal #20882"""
        super(TestImportJournal, self).setUp()
        self.journal_obj = self.env["account.journal"]
        self.acc_obj = self.env["account.account"]
        self.analytic_acc_obj = self.env["account.analytic.account"]
        self.journal = self.journal_obj.create(
            {"name": "test journal", "type": "general", "code": "123"}
        )
        self.receivable_account = self.acc_obj.create(
            {
                "name": "receivable account",
                "code": "test12345",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.payable_account = self.acc_obj.create(
            {
                "name": "payable account",
                "code": "test6789",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        self.a1 = self.acc_obj.create(
            {
                "name": "a1",
                "code": "2100",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a2 = self.acc_obj.create(
            {
                "name": "a2",
                "code": "2105",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a3 = self.acc_obj.create(
            {
                "name": "a3",
                "code": "2156",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a4 = self.acc_obj.create(
            {
                "name": "a4",
                "code": "2157",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a5 = self.acc_obj.create(
            {
                "name": "a5",
                "code": "4000",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a6 = self.acc_obj.create(
            {
                "name": "a6",
                "code": "4001",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a7 = self.acc_obj.create(
            {
                "name": "a7",
                "code": "4020",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.a8 = self.acc_obj.create(
            {
                "name": "a8",
                "code": "4021",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.analytic_account_1 = self.env["account.analytic.account"].create(
            {
                "name": "Test AA 1",
                "code": "P001",
            }
        )
        self.analytic_account_2 = self.env["account.analytic.account"].create(
            {
                "name": "Test AA 2",
                "code": "P002",
            }
        )

        self.receivable_account_analytic = self.analytic_acc_obj.create(
            {"name": "receivable account", "code": "testan12345"}
        )
        self.payable_account_analytic = self.analytic_acc_obj.create(
            {"name": "payable account", "code": "testan6789"}
        )
        self.import_journal = self.env["wizard.import.journal"]
        self.test_path = os.path.dirname(os.path.realpath(__file__))
        self.sample_path = os.path.join(self.test_path, "test_files")
        csv_path = os.path.join(self.sample_path, "nmbrs-testfile-without-analytic.csv")
        self.csv_data = ""
        with open(csv_path, "rb") as csv_file:
            self.csv_data = csv_file.read()

        csv_with_analytic_path = os.path.join(
            self.sample_path, "nmbrs-testfile-with-analytic.csv"
        )
        self.csv_with_analytic_data = ""

        with open(csv_with_analytic_path, "rb") as csv_with_analytic_file:
            self.csv_with_analytic_data = csv_with_analytic_file.read()

    def test_import_with_analytic_account(self, product=None, picking=None):
        """test for import journal with analytic account #20882"""
        import_journal_id = self.import_journal.create(
            {
                "data_file": base64.encodebytes(self.csv_with_analytic_data),
                "reference": "test_reference",
                "date": fields.Date.today(),
                "including_analytic_account": True,
                "journal_id": self.journal.id,
            }
        )
        journal_entry = import_journal_id.import_file()
        self.assertTrue(journal_entry)

    def test_import_without_analytic_account(self, product=None, picking=None):
        """test for import journal without analytic account #20882"""
        import_journal_id = self.import_journal.create(
            {
                "data_file": base64.encodebytes(self.csv_data),
                "reference": "test_reference",
                "date": fields.Date.today(),
                "including_analytic_account": False,
                "journal_id": self.journal.id,
            }
        )
        journal_entry = import_journal_id.import_file()
        self.assertTrue(journal_entry)
