from odoo import models, fields, api


class LibraryBook(models.Model):

    _name = "library.book"
    _description = "Book"
    # Add chatter functionality for messaging and activity tracking.
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # This specifies the field to display as the main name for the record in the form view.
    _rec_name = 'display_name'
    # Compute field to display a formatted name for the record, combining 'name' and 'author' fields for better readability.
    display_name = fields.Char(compute='_compute_display_name')
    # Field to control the visibility of the record (archive functionality). Default value is set to True, meaning records are active by default.
    active = fields.Boolean(default='true')
    ref = fields.Char(
        default='New',
        readonly=1
    )
    name = fields.Char(string="Title", required=True)
    author = fields.Char(string="Author", required=True)
    publisher = fields.Char(string="Publisher")
    description = fields.Text(string="Description")
    publication_date = fields.Date(string="Publication Date")
    selling_price = fields.Float()
    category_id = fields.Many2one('library.category', string="Category")

    expected_sealing_date = fields.Date(string="Expected Sealing Date")
    is_late = fields.Boolean(string="Late Sealing")

    state = fields.Selection(
        string="Status",
        selection=[
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("borrowed", "Borrowed"),
            ("damaged", "Damaged"),
        ],
        default="available",
    )

    _sql_constraints = [
        ('unique_name', 'unique("name")', 'This name is exist!')]

    def print_xlsx(self):
        print("test")
        return {
            'type': 'ir.actions.act_url',
            'url': '/book/excel/report',
            'target': 'new'
        }

    def action_available(self):
        for rec in self:
            rec.state = "available"
            rec.is_late = False
            if rec.expected_sealing_date:
                rec.expected_sealing_date = False

    def action_reserved(self):
        for rec in self:
            rec.state = "reserved"

    def action_borrowed(self):
        for rec in self:
            rec.is_late = False
            rec.state = "borrowed"
            if (
                rec.expected_sealing_date
                and rec.expected_sealing_date < fields.date.today()
            ):
                rec.is_late = True
            rec.expected_sealing_date = False

    def action_damaged(self):
        for rec in self:
            rec.state = "damaged"
            rec.is_late = False
            if rec.expected_sealing_date:
                rec.expected_sealing_date = False

    def check_sealing_date(self):
        book_ids = self.search([])
        for rec in book_ids:
            if (
                rec.expected_sealing_date
                and rec.expected_sealing_date < fields.date.today()
                and rec.state != "borrowed"
            ):
                rec.is_late = True

    @api.depends('name', 'author')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} ({rec.author})"

    line_number = fields.Integer(string='Line Number', default=10)

    @api.model
    def create(self, vals):
        res = super(LibraryBook, self).create(vals)
        res.ref = self.env['ir.sequence'].next_by_code('book_seq')
        return res
