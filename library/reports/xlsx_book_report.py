from odoo import http
from odoo.http import request
import io
import xlsxwriter
# we can use any external library


class XlsxBookReport(http.Controller):
    @http.route('/book/excel/report', type='http', auth='user')
    def download_book_excel_report(self):
        print('before the request')
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Book')

        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        headers = ['ref', 'name', 'author', 'selling_price']

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # You can add your data rows here
        # Example: worksheet.write(row, col, data)

        workbook.close()
        output.seek(0)

        # Changed space to underscore for a better file name
        file_name = "books_report.xlsx"
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={file_name}')
            ]
        )


