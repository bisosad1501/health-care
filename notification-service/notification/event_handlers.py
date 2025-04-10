"""
Event handlers for processing events from other services.
"""
import logging
from django.utils import timezone
from .models import Notification
from .tasks import send_email_notification, send_sms_notification

logger = logging.getLogger(__name__)


def process_appointment_event(event_data):
    """
    Process events from the Appointment Service.
    """
    event_type = event_data.get('event_type')
    appointment_id = event_data.get('appointment_id')
    patient_id = event_data.get('patient_id')
    doctor_id = event_data.get('doctor_id')
    appointment_date = event_data.get('appointment_date')
    appointment_type = event_data.get('appointment_type')
    notes = event_data.get('notes', '')

    # Format appointment date for display
    formatted_date = appointment_date if appointment_date else 'Unknown'

    # Create notifications based on event type
    if event_type == 'CREATED':
        # Notify patient about new appointment
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject=f'New Appointment Scheduled: {appointment_type}',
            content=f'Your appointment has been scheduled for {formatted_date}. ' +
                    f'Appointment type: {appointment_type}. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        # Notify doctor about new appointment
        doctor_notification = Notification(
            recipient_id=doctor_id,
            recipient_type='DOCTOR',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject=f'New Appointment Scheduled: {appointment_type}',
            content=f'A new appointment has been scheduled for {formatted_date}. ' +
                    f'Appointment type: {appointment_type}. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        doctor_notification.save()
        send_email_notification.delay(doctor_notification.id)

        return {
            'message': 'Appointment creation notifications sent',
            'notifications': [patient_notification.id, doctor_notification.id]
        }

    elif event_type == 'UPDATED':
        # Notify patient about updated appointment
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject=f'Appointment Updated: {appointment_type}',
            content=f'Your appointment has been updated to {formatted_date}. ' +
                    f'Appointment type: {appointment_type}. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        # Notify doctor about updated appointment
        doctor_notification = Notification(
            recipient_id=doctor_id,
            recipient_type='DOCTOR',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject=f'Appointment Updated: {appointment_type}',
            content=f'An appointment has been updated to {formatted_date}. ' +
                    f'Appointment type: {appointment_type}. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        doctor_notification.save()
        send_email_notification.delay(doctor_notification.id)

        return {
            'message': 'Appointment update notifications sent',
            'notifications': [patient_notification.id, doctor_notification.id]
        }

    elif event_type == 'CANCELLED':
        # Notify patient about cancelled appointment
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject='Appointment Cancelled',
            content=f'Your appointment scheduled for {formatted_date} has been cancelled. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        # Notify doctor about cancelled appointment
        doctor_notification = Notification(
            recipient_id=doctor_id,
            recipient_type='DOCTOR',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject='Appointment Cancelled',
            content=f'An appointment scheduled for {formatted_date} has been cancelled. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        doctor_notification.save()
        send_email_notification.delay(doctor_notification.id)

        return {
            'message': 'Appointment cancellation notifications sent',
            'notifications': [patient_notification.id, doctor_notification.id]
        }

    elif event_type == 'REMINDER':
        # Send reminder to patient
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject='Appointment Reminder',
            content=f'Reminder: You have an appointment scheduled for {formatted_date}. ' +
                    f'Appointment type: {appointment_type}. ' +
                    (f'Notes: {notes}' if notes else ''),
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        # Also send SMS reminder if configured
        patient_sms = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='SMS',
            subject='',
            content=f'Reminder: You have an appointment scheduled for {formatted_date}.',
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_sms.save()
        send_sms_notification.delay(patient_sms.id)

        return {
            'message': 'Appointment reminder notifications sent',
            'notifications': [patient_notification.id, patient_sms.id]
        }

    elif event_type == 'COMPLETED':
        # Notify patient about completed appointment
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='APPOINTMENT',
            channel='EMAIL',
            subject='Appointment Completed',
            content=f'Your appointment on {formatted_date} has been marked as completed. ' +
                    'Thank you for visiting our healthcare facility.',
            reference_id=str(appointment_id),
            reference_type='APPOINTMENT',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Appointment completion notification sent',
            'notifications': [patient_notification.id]
        }

    else:
        logger.warning(f"Unknown appointment event type: {event_type}")
        return {
            'message': f'Unknown appointment event type: {event_type}',
            'notifications': []
        }


def process_medical_record_event(event_data):
    """
    Process events from the Medical Record Service.
    """
    event_type = event_data.get('event_type')
    record_id = event_data.get('record_id')
    patient_id = event_data.get('patient_id')
    doctor_id = event_data.get('doctor_id')
    record_type = event_data.get('record_type')
    description = event_data.get('description', '')

    # Create notifications based on event type
    if event_type == 'CREATED':
        # Notify patient about new medical record
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='MEDICAL_RECORD',
            channel='EMAIL',
            subject='New Medical Record Created',
            content=f'A new medical record has been created for you. ' +
                    f'Record type: {record_type}. ' +
                    (f'Description: {description}' if description else ''),
            reference_id=str(record_id),
            reference_type='MEDICAL_RECORD',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Medical record creation notification sent',
            'notifications': [patient_notification.id]
        }

    elif event_type == 'UPDATED':
        # Notify patient about updated medical record
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='MEDICAL_RECORD',
            channel='EMAIL',
            subject='Medical Record Updated',
            content=f'Your medical record has been updated. ' +
                    f'Record type: {record_type}. ' +
                    (f'Description: {description}' if description else ''),
            reference_id=str(record_id),
            reference_type='MEDICAL_RECORD',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Medical record update notification sent',
            'notifications': [patient_notification.id]
        }

    elif event_type == 'DIAGNOSIS_ADDED':
        # Notify patient about new diagnosis
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='MEDICAL_RECORD',
            channel='EMAIL',
            subject='New Diagnosis Added to Your Medical Record',
            content=f'A new diagnosis has been added to your medical record. ' +
                    (f'Details: {description}' if description else ''),
            reference_id=str(record_id),
            reference_type='MEDICAL_RECORD',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Diagnosis notification sent',
            'notifications': [patient_notification.id]
        }

    elif event_type == 'TREATMENT_ADDED':
        # Notify patient about new treatment
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='MEDICAL_RECORD',
            channel='EMAIL',
            subject='New Treatment Added to Your Medical Record',
            content=f'A new treatment has been added to your medical record. ' +
                    (f'Details: {description}' if description else ''),
            reference_id=str(record_id),
            reference_type='MEDICAL_RECORD',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Treatment notification sent',
            'notifications': [patient_notification.id]
        }

    elif event_type == 'MEDICATION_ADDED':
        # Notify patient about new medication
        patient_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='MEDICAL_RECORD',
            channel='EMAIL',
            subject='New Medication Added to Your Medical Record',
            content=f'A new medication has been added to your medical record. ' +
                    (f'Details: {description}' if description else ''),
            reference_id=str(record_id),
            reference_type='MEDICAL_RECORD',
            status='PENDING'
        )
        patient_notification.save()
        send_email_notification.delay(patient_notification.id)

        return {
            'message': 'Medication notification sent',
            'notifications': [patient_notification.id]
        }

    else:
        logger.warning(f"Unknown medical record event type: {event_type}")
        return {
            'message': f'Unknown medical record event type: {event_type}',
            'notifications': []
        }


def process_billing_event(event_data):
    """
    Process events from the Billing Service.
    """
    event_type = event_data.get('event_type')
    invoice_id = event_data.get('invoice_id')
    payment_id = event_data.get('payment_id')
    claim_id = event_data.get('claim_id')
    patient_id = event_data.get('patient_id')
    amount = event_data.get('amount')
    due_date = event_data.get('due_date')
    description = event_data.get('description', '')

    # Format amount for display
    formatted_amount = f"{amount:,.0f} VND" if amount else "Không xác định"

    # Format due date for display
    formatted_due_date = due_date.strftime('%d/%m/%Y') if due_date else 'Không xác định'

    # Create notifications based on event type
    if event_type == 'INVOICE_CREATED':
        # Notify patient about new invoice
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Hóa đơn mới đã được tạo',
            content=f'Một hóa đơn mới đã được tạo cho bạn. ' +
                    f'Số tiền: {formatted_amount}. ' +
                    f'Ngày đến hạn: {formatted_due_date}. ' +
                    (f'Mô tả: {description}' if description else ''),
            reference_id=str(invoice_id),
            reference_type='INVOICE',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo tạo hóa đơn',
            'notifications': [notification.id]
        }

    elif event_type == 'PAYMENT_RECEIVED':
        # Notify patient about payment received
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Đã nhận thanh toán',
            content=f'Chúng tôi đã nhận được khoản thanh toán của bạn với số tiền {formatted_amount}. ' +
                    'Cảm ơn bạn đã thanh toán.',
            reference_id=str(payment_id),
            reference_type='PAYMENT',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo nhận thanh toán',
            'notifications': [notification.id]
        }

    elif event_type == 'PAYMENT_DUE':
        # Notify patient about payment due
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Nhắc nhở thanh toán',
            content=f'Đây là lời nhắc rằng khoản thanh toán của bạn với số tiền {formatted_amount} sẽ đến hạn vào ngày {formatted_due_date}. ' +
                    'Vui lòng thanh toán trước ngày đến hạn để tránh phí trễ hạn.',
            reference_id=str(invoice_id),
            reference_type='INVOICE',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also send SMS reminder
        sms_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='SMS',
            subject='',
            content=f'Nhắc nhở: Khoản thanh toán của bạn với số tiền {formatted_amount} sẽ đến hạn vào ngày {formatted_due_date}.',
            reference_id=str(invoice_id),
            reference_type='INVOICE',
            status='PENDING'
        )
        sms_notification.save()
        send_sms_notification.delay(sms_notification.id)

        return {
            'message': 'Đã gửi thông báo nhắc nhở thanh toán',
            'notifications': [notification.id, sms_notification.id]
        }

    elif event_type == 'PAYMENT_OVERDUE':
        # Notify patient about overdue payment
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Thanh toán quá hạn',
            content=f'Khoản thanh toán của bạn với số tiền {formatted_amount} đã đến hạn vào ngày {formatted_due_date} và hiện đã quá hạn. ' +
                    'Vui lòng thanh toán càng sớm càng tốt để tránh các khoản phí bổ sung.',
            reference_id=str(invoice_id),
            reference_type='INVOICE',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also send SMS reminder for overdue payment
        sms_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='SMS',
            subject='',
            content=f'KHẨN CẤP: Khoản thanh toán của bạn với số tiền {formatted_amount} đã quá hạn. Vui lòng thanh toán ngay lập tức.',
            reference_id=str(invoice_id),
            reference_type='INVOICE',
            status='PENDING'
        )
        sms_notification.save()
        send_sms_notification.delay(sms_notification.id)

        return {
            'message': 'Đã gửi thông báo thanh toán quá hạn',
            'notifications': [notification.id, sms_notification.id]
        }

    elif event_type == 'INSURANCE_CLAIM_SUBMITTED':
        # Notify patient about insurance claim submission
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Đã gửi yêu cầu bảo hiểm',
            content=f'Một yêu cầu bảo hiểm đã được gửi cho hóa đơn của bạn. ' +
                    f'Số tiền yêu cầu: {formatted_amount}. ' +
                    'Chúng tôi sẽ thông báo cho bạn khi nhận được phản hồi từ nhà cung cấp bảo hiểm của bạn.',
            reference_id=str(claim_id),
            reference_type='CLAIM',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo yêu cầu bảo hiểm',
            'notifications': [notification.id]
        }

    elif event_type == 'INSURANCE_CLAIM_APPROVED':
        # Notify patient about approved insurance claim
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Yêu cầu bảo hiểm đã được chấp nhận',
            content=f'Yêu cầu bảo hiểm của bạn đã được chấp nhận. ' +
                    f'Số tiền được chấp nhận: {formatted_amount}. ' +
                    'Số tiền được chấp nhận sẽ được áp dụng vào hóa đơn của bạn.',
            reference_id=str(claim_id),
            reference_type='CLAIM',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo chấp nhận yêu cầu bảo hiểm',
            'notifications': [notification.id]
        }

    elif event_type == 'INSURANCE_CLAIM_REJECTED':
        # Notify patient about rejected insurance claim
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='BILLING',
            channel='EMAIL',
            subject='Yêu cầu bảo hiểm đã bị từ chối',
            content=f'Yêu cầu bảo hiểm của bạn đã bị từ chối. ' +
                    f'Số tiền yêu cầu: {formatted_amount}. ' +
                    'Vui lòng liên hệ với bộ phận thanh toán của chúng tôi để biết thêm thông tin và thảo luận về các tùy chọn thanh toán.',
            reference_id=str(claim_id),
            reference_type='CLAIM',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo từ chối yêu cầu bảo hiểm',
            'notifications': [notification.id]
        }

    else:
        logger.warning(f"Unknown billing event type: {event_type}")
        return {
            'message': f'Loại sự kiện thanh toán không xác định: {event_type}',
            'notifications': []
        }


def process_pharmacy_event(event_data):
    """
    Process events from the Pharmacy Service.
    """
    event_type = event_data.get('event_type')
    prescription_id = event_data.get('prescription_id')
    medication_id = event_data.get('medication_id')
    patient_id = event_data.get('patient_id')
    doctor_id = event_data.get('doctor_id')
    medication_name = event_data.get('medication_name', '')
    pickup_date = event_data.get('pickup_date')
    refill_date = event_data.get('refill_date')
    notes = event_data.get('notes', '')

    # Format dates for display
    formatted_pickup_date = pickup_date if pickup_date else 'Không xác định'
    formatted_refill_date = refill_date if refill_date else 'Không xác định'

    # Create notifications based on event type
    if event_type == 'PRESCRIPTION_CREATED':
        # Notify patient about new prescription
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Đơn thuốc mới đã được tạo',
            content=f'Một đơn thuốc mới đã được tạo cho bạn. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    (f'Ghi chú: {notes}' if notes else ''),
            reference_id=str(prescription_id),
            reference_type='PRESCRIPTION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo tạo đơn thuốc',
            'notifications': [notification.id]
        }

    elif event_type == 'PRESCRIPTION_FILLED':
        # Notify patient about filled prescription
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Đơn thuốc đã được chuẩn bị',
            content=f'Đơn thuốc của bạn đã được chuẩn bị và đang được xử lý. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    'Chúng tôi sẽ thông báo cho bạn khi đơn thuốc sẵn sàng để lấy.',
            reference_id=str(prescription_id),
            reference_type='PRESCRIPTION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo chuẩn bị đơn thuốc',
            'notifications': [notification.id]
        }

    elif event_type == 'PRESCRIPTION_READY':
        # Notify patient about prescription ready for pickup
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Đơn thuốc sẵn sàng để lấy',
            content=f'Đơn thuốc của bạn đã sẵn sàng để lấy. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    (f'Ngày lấy: {formatted_pickup_date}. ' if pickup_date else '') +
                    'Vui lòng mang theo giấy tờ tùy thân khi đến lấy thuốc.',
            reference_id=str(prescription_id),
            reference_type='PRESCRIPTION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also send SMS notification
        sms_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='SMS',
            subject='',
            content=f'Đơn thuốc của bạn đã sẵn sàng để lấy tại nhà thuốc của chúng tôi.' +
                    (f' Thuốc: {medication_name}.' if medication_name else ''),
            reference_id=str(prescription_id),
            reference_type='PRESCRIPTION',
            status='PENDING'
        )
        sms_notification.save()
        send_sms_notification.delay(sms_notification.id)

        return {
            'message': 'Đã gửi thông báo đơn thuốc sẵn sàng',
            'notifications': [notification.id, sms_notification.id]
        }

    elif event_type == 'PRESCRIPTION_PICKED_UP':
        # Notify patient about picked up prescription
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Đơn thuốc đã được lấy',
            content=f'Đơn thuốc của bạn đã được lấy thành công. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    'Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.',
            reference_id=str(prescription_id),
            reference_type='PRESCRIPTION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo đơn thuốc đã được lấy',
            'notifications': [notification.id]
        }

    elif event_type == 'MEDICATION_REFILL_DUE':
        # Notify patient about medication refill due
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Nhắc nhở tái cấp thuốc',
            content=f'Đây là lời nhắc rằng thuốc của bạn sẽ cần được tái cấp vào ngày {formatted_refill_date}. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    'Vui lòng liên hệ với bác sĩ của bạn để được kê đơn mới hoặc tái cấp thuốc.',
            reference_id=str(medication_id),
            reference_type='MEDICATION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also send SMS reminder
        sms_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='SMS',
            subject='',
            content=f'Nhắc nhở: Thuốc của bạn ({medication_name}) sẽ cần được tái cấp vào ngày {formatted_refill_date}.',
            reference_id=str(medication_id),
            reference_type='MEDICATION',
            status='PENDING'
        )
        sms_notification.save()
        send_sms_notification.delay(sms_notification.id)

        return {
            'message': 'Đã gửi thông báo nhắc nhở tái cấp thuốc',
            'notifications': [notification.id, sms_notification.id]
        }

    elif event_type == 'MEDICATION_EXPIRING':
        # Notify patient about expiring medication
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='PHARMACY',
            channel='EMAIL',
            subject='Thuốc sắp hết hạn',
            content=f'Thuốc của bạn sắp hết hạn. ' +
                    (f'Thuốc: {medication_name}. ' if medication_name else '') +
                    'Vui lòng kiểm tra ngày hết hạn trên bao bì và liên hệ với bác sĩ của bạn nếu cần đơn thuốc mới.',
            reference_id=str(medication_id),
            reference_type='MEDICATION',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo thuốc sắp hết hạn',
            'notifications': [notification.id]
        }

    else:
        logger.warning(f"Unknown pharmacy event type: {event_type}")
        return {
            'message': f'Loại sự kiện nhà thuốc không xác định: {event_type}',
            'notifications': []
        }


def process_laboratory_event(event_data):
    """
    Process events from the Laboratory Service.
    """
    event_type = event_data.get('event_type')
    test_id = event_data.get('test_id')
    result_id = event_data.get('result_id')
    patient_id = event_data.get('patient_id')
    doctor_id = event_data.get('doctor_id')
    test_name = event_data.get('test_name', '')
    test_date = event_data.get('test_date')
    is_abnormal = event_data.get('is_abnormal')
    notes = event_data.get('notes', '')

    # Format date for display
    formatted_test_date = test_date if test_date else 'Không xác định'

    # Create notifications based on event type
    if event_type == 'TEST_ORDERED':
        # Notify patient about ordered test
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='EMAIL',
            subject='Xét nghiệm mới đã được yêu cầu',
            content=f'Một xét nghiệm mới đã được yêu cầu cho bạn. ' +
                    (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                    (f'Ngày xét nghiệm: {formatted_test_date}. ' if test_date else '') +
                    (f'Ghi chú: {notes}' if notes else ''),
            reference_id=str(test_id),
            reference_type='TEST',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo yêu cầu xét nghiệm',
            'notifications': [notification.id]
        }

    elif event_type == 'SAMPLE_COLLECTED':
        # Notify patient about sample collection
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='EMAIL',
            subject='Mẫu xét nghiệm đã được thu thập',
            content=f'Mẫu xét nghiệm của bạn đã được thu thập. ' +
                    (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                    'Chúng tôi sẽ thông báo cho bạn khi kết quả sẵn sàng.',
            reference_id=str(test_id),
            reference_type='TEST',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo thu thập mẫu',
            'notifications': [notification.id]
        }

    elif event_type == 'RESULTS_READY':
        # Notify patient about ready results
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='EMAIL',
            subject='Kết quả xét nghiệm đã sẵn sàng',
            content=f'Kết quả xét nghiệm của bạn đã sẵn sàng. ' +
                    (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                    'Vui lòng đăng nhập vào tài khoản của bạn để xem kết quả hoặc liên hệ với bác sĩ của bạn.',
            reference_id=str(result_id),
            reference_type='RESULT',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also notify doctor if results are abnormal
        if is_abnormal and doctor_id:
            doctor_notification = Notification(
                recipient_id=doctor_id,
                recipient_type='DOCTOR',
                notification_type='LABORATORY',
                channel='EMAIL',
                subject='Kết quả xét nghiệm bất thường',
                content=f'Kết quả xét nghiệm bất thường đã được phát hiện cho bệnh nhân (ID: {patient_id}). ' +
                        (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                        'Vui lòng xem xét kết quả và liên hệ với bệnh nhân nếu cần thiết.',
                reference_id=str(result_id),
                reference_type='RESULT',
                status='PENDING'
            )
            doctor_notification.save()
            send_email_notification.delay(doctor_notification.id)

            return {
                'message': 'Đã gửi thông báo kết quả sẵn sàng (bất thường)',
                'notifications': [notification.id, doctor_notification.id]
            }

        return {
            'message': 'Đã gửi thông báo kết quả sẵn sàng',
            'notifications': [notification.id]
        }

    elif event_type == 'RESULTS_DELIVERED':
        # Notify patient about delivered results
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='EMAIL',
            subject='Kết quả xét nghiệm đã được gửi',
            content=f'Kết quả xét nghiệm của bạn đã được gửi. ' +
                    (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                    'Vui lòng kiểm tra email của bạn hoặc đăng nhập vào tài khoản của bạn để xem kết quả.',
            reference_id=str(result_id),
            reference_type='RESULT',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        return {
            'message': 'Đã gửi thông báo kết quả đã được gửi',
            'notifications': [notification.id]
        }

    elif event_type == 'ABNORMAL_RESULTS':
        # Notify patient about abnormal results
        notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='EMAIL',
            subject='Kết quả xét nghiệm bất thường',
            content=f'Kết quả xét nghiệm của bạn có một số giá trị bất thường. ' +
                    (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                    'Vui lòng liên hệ với bác sĩ của bạn để thảo luận về kết quả này.',
            reference_id=str(result_id),
            reference_type='RESULT',
            status='PENDING'
        )
        notification.save()
        send_email_notification.delay(notification.id)

        # Also send SMS for abnormal results
        sms_notification = Notification(
            recipient_id=patient_id,
            recipient_type='PATIENT',
            notification_type='LABORATORY',
            channel='SMS',
            subject='',
            content=f'QUAN TRỌNG: Kết quả xét nghiệm của bạn có một số giá trị bất thường. Vui lòng liên hệ với bác sĩ của bạn.',
            reference_id=str(result_id),
            reference_type='RESULT',
            status='PENDING'
        )
        sms_notification.save()
        send_sms_notification.delay(sms_notification.id)

        # Also notify doctor about abnormal results
        if doctor_id:
            doctor_notification = Notification(
                recipient_id=doctor_id,
                recipient_type='DOCTOR',
                notification_type='LABORATORY',
                channel='EMAIL',
                subject='Kết quả xét nghiệm bất thường',
                content=f'Kết quả xét nghiệm bất thường đã được phát hiện cho bệnh nhân (ID: {patient_id}). ' +
                        (f'Tên xét nghiệm: {test_name}. ' if test_name else '') +
                        'Vui lòng xem xét kết quả và liên hệ với bệnh nhân.',
                reference_id=str(result_id),
                reference_type='RESULT',
                status='PENDING'
            )
            doctor_notification.save()
            send_email_notification.delay(doctor_notification.id)

            return {
                'message': 'Đã gửi thông báo kết quả bất thường',
                'notifications': [notification.id, sms_notification.id, doctor_notification.id]
            }

        return {
            'message': 'Đã gửi thông báo kết quả bất thường',
            'notifications': [notification.id, sms_notification.id]
        }

    else:
        logger.warning(f"Unknown laboratory event type: {event_type}")
        return {
            'message': f'Loại sự kiện phòng xét nghiệm không xác định: {event_type}',
            'notifications': []
        }
