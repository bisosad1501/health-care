"""
Module for generating PDF invoices.
"""
import os
import logging
from io import BytesIO
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.utils.translation import gettext as _
from xhtml2pdf import pisa

from .models import Invoice

logger = logging.getLogger(__name__)


def render_to_pdf(template_src, context_dict={}):
    """
    Render HTML template to PDF.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    logger.error(f"Error generating PDF: {pdf.err}")
    return None


def generate_invoice_pdf(invoice_id):
    """
    Generate PDF for an invoice.
    """
    try:
        # Get invoice data
        invoice = Invoice.objects.get(id=invoice_id)
        
        # Format currency values
        def format_currency(value):
            if value is None:
                return "0 VND"
            return f"{int(value):,} VND".replace(",", ".")
        
        # Format date values
        def format_date(date_obj):
            if date_obj is None:
                return ""
            return date_obj.strftime("%d/%m/%Y")
        
        # Prepare context for PDF template
        context = {
            'invoice': invoice,
            'items': invoice.items.all(),
            'payments': invoice.payments.all(),
            'insurance_claims': invoice.insurance_claims.all(),
            'total_amount': format_currency(invoice.total_amount),
            'discount': format_currency(invoice.discount),
            'tax': format_currency(invoice.tax),
            'final_amount': format_currency(invoice.final_amount),
            'issue_date': format_date(invoice.issue_date),
            'due_date': format_date(invoice.due_date),
            'current_date': datetime.now().strftime("%d/%m/%Y"),
            'logo_path': os.path.join(settings.STATIC_ROOT, 'billing/images/logo.png'),
            'hospital_name': 'Hệ thống Y tế',
            'hospital_address': '123 Đường Y tế, Quận 1, TP.HCM',
            'hospital_phone': '(028) 1234 5678',
            'hospital_email': 'info@healthcare.com',
            'hospital_website': 'www.healthcare.com',
        }
        
        # Calculate total paid amount
        total_paid = sum(payment.amount for payment in invoice.payments.all())
        context['total_paid'] = format_currency(total_paid)
        context['balance'] = format_currency(invoice.final_amount - total_paid)
        
        # Generate PDF
        pdf = render_to_pdf('billing/invoice_pdf.html', context)
        return pdf
    except Invoice.DoesNotExist:
        logger.error(f"Invoice with ID {invoice_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error generating invoice PDF: {str(e)}")
        return None
