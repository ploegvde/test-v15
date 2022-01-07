# See LICENSE file for full copyright and licensing details.
import base64
import codecs
import csv
import io
import os
import tempfile

from odoo import _, api, fields, models
from odoo.exceptions import UserError

encoding = "utf-8"


class WizardImportJournal(models.TransientModel):
    _name = "wizard.import.journal"
    _description = "Import journal"

    # 22635 :  Migratie to V15
    data_file = fields.Binary(string="Export Filename")
    filename = fields.Char(string="File Name", size=256)
    date = fields.Date(string="Date")
    reference = fields.Char(string="Reference", size=64)
    including_analytic_account = fields.Boolean(
        "Including Analytic Account", default=False
    )

    @api.model
    def default_get_journal(self):
        """method for fetch last saved value from system parameter #20882"""
        journal_id = self.env["ir.config_parameter"].sudo().get_param("journal_id")
        # check the user's company for journal setup
        if self.env.user.company_id:
            return False
        return int(journal_id)

    def default_set_journal(self):
        """method for set system parameter of journal #20882"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .set_param("journal_id", self.journal_id.id)
        )

    journal_id = fields.Many2one(
        "account.journal", "Journal", default=default_get_journal
    )

    def import_file(self):
        """import csv files with and without analytic data #20882"""
        try:
            journal_obj = self.env["account.move"]
            data = base64.b64decode(self.data_file)
            data = data.decode(encoding, errors="ignore")
            data_vals = {}
            vals = []
            if data.count("\x00"):
                my_csv_temp = tempfile.NamedTemporaryFile(mode="w", delete=False)
                for line in data:
                    my_csv_temp.write(line.replace("\x00", ""))
                my_csv_temp.close()

                with codecs.open(my_csv_temp.name, "rb", encoding) as mycsvfile:
                    reader = csv.reader(mycsvfile, delimiter=";")
                    self.default_set_journal()
                    vals = self.get_line_vals(reader)
                os.unlink(my_csv_temp.name)
            else:
                st = io.StringIO(data)
                reader = csv.reader(st, delimiter=";")
                self.default_set_journal()
                vals = self.get_line_vals(reader)
        except UserError:
            raise
        except Exception:
            raise UserError(_("Please import proper format file."))
        data_vals["line_ids"] = [[0, 0, line] for line in vals]
        data_vals["journal_id"] = self.journal_id.id
        data_vals["ref"] = self.reference
        data_vals["date"] = self.date
        res = journal_obj.create(data_vals)
        if not res:
            return
        imd = self.env["ir.model.data"]
        # change function name xmlid_to_res_id to _xmlid_to_res_id according to v15 #22635
        list_view_id = imd._xmlid_to_res_id("account.view_move_tree")
        form_view_id = imd._xmlid_to_res_id("account.view_move_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "=", res.id]],
            "name": _("Journal Entries"),
        }

    def get_line_vals(self, reader):
        """get line_ids values #20882"""
        acc_obj = self.env["account.account"]
        analytic_acc_obj = self.env["account.analytic.account"]
        check_header = False
        vals = []
        for row in reader:
            check_header = row[5]
            break
        for row in reader:
            # if Including Analytic Account boolean true and 'Kostenplaats' header value get
            if self.including_analytic_account and check_header == "Kostenplaats":
                analytic_code = row[5].split("|")[0]
                if analytic_code.replace(" ", "") == "0":
                    continue
                analytic_acc_id = analytic_acc_obj.search(
                    [("code", "=", analytic_code.replace(" ", ""))],
                    limit=1,
                )
                if not analytic_acc_id:
                    raise UserError(
                        _(
                            "Analytic account '%s' is not found."
                            + " Please create it first."
                        )
                        % analytic_code
                    )
                account_id = acc_obj.search([("code", "=", row[6])], limit=1)
                if not account_id:
                    raise UserError(_("No Account found for the code '%s'.") % row[6])
                vals.append(
                    {
                        "account_id": account_id.id,
                        "analytic_account_id": analytic_acc_id.id,
                        "name": row[7],
                        "debit": float(row[8].replace(",", ".")),
                        "credit": float(row[9].replace(",", ".")),
                    }
                )

            elif check_header == "Grootboeknr" and not self.including_analytic_account:
                account_id = acc_obj.search([("code", "=", row[5])], limit=1).id
                if not account_id:
                    raise UserError(_("No Account found for the code '%s'.") % row[5])
                vals.append(
                    {
                        "account_id": account_id,
                        "name": row[6],
                        "debit": float(row[7].replace(",", ".")),
                        "credit": float(row[8].replace(",", ".")),
                    }
                )
            else:
                raise UserError(_("Please import proper format file."))
        return vals
