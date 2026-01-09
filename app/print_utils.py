from datetime import datetime

from fpdf import FPDF


def _safe_text(value) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    return text.encode("latin-1", "replace").decode("latin-1")


def _fmt_dt(value) -> str:
    if not value:
        return "N/A"
    return value.strftime("%Y-%m-%d %H:%M")


def _output_pdf(pdf: FPDF) -> bytes:
    return pdf.output(dest="S").encode("latin-1")


def _init_pdf(title: str) -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _safe_text(title), ln=True)
    pdf.set_font("Helvetica", "", 11)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 7, _safe_text(f"Generated: {timestamp}"), ln=True)
    pdf.ln(2)
    return pdf


def _add_section_title(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _safe_text(title), ln=True)
    pdf.set_font("Helvetica", "", 11)


def _add_key_value(pdf: FPDF, label: str, value: str) -> None:
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(42, 6, _safe_text(f"{label}:"), 0, 0)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _safe_text(value))


def find_latest_delivered_event(shipment):
    if not shipment or not shipment.tracking_events:
        return None
    for event in reversed(shipment.tracking_events):
        if event.status == "Delivered":
            return event
    return None


def build_shipment_pdf(shipment) -> bytes:
    pdf = _init_pdf("Shipment Summary")
    customer = shipment.customer
    courier = shipment.courier

    _add_section_title(pdf, "Shipment Details")
    _add_key_value(pdf, "Tracking Number", shipment.tracking_number)
    _add_key_value(pdf, "Status", shipment.latest_status())
    _add_key_value(pdf, "Requested", _fmt_dt(shipment.requested_date))
    _add_key_value(pdf, "Sender Address", shipment.sender_address)
    _add_key_value(pdf, "Receiver Address", shipment.receiver_address)
    _add_key_value(pdf, "City", shipment.city or "N/A")
    _add_key_value(
        pdf,
        "Customer",
        f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
    )
    _add_key_value(
        pdf,
        "Courier",
        f"{courier.first_name} {courier.last_name}" if courier else "Unassigned",
    )

    pdf.ln(2)
    _add_section_title(pdf, "Tracking Timeline")
    if not shipment.tracking_events:
        pdf.cell(0, 6, "No tracking events.", ln=True)
        return _output_pdf(pdf)

    for event in shipment.tracking_events:
        line = f"{_fmt_dt(event.created_at)} - {event.status} - {event.location_description}"
        pdf.multi_cell(0, 6, _safe_text(line))
        if event.notes:
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 5, _safe_text(f"Notes: {event.notes}"))
            pdf.set_font("Helvetica", "", 11)
        if event.proof_url:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, _safe_text(f"Proof: {event.proof_url}"))
            pdf.set_font("Helvetica", "", 11)
        pdf.ln(1)

    return _output_pdf(pdf)


def build_receipt_pdf(shipment, delivered_event) -> bytes:
    pdf = _init_pdf("Delivery Receipt")
    customer = shipment.customer
    courier = shipment.courier

    _add_section_title(pdf, "Receipt Details")
    _add_key_value(pdf, "Tracking Number", shipment.tracking_number)
    _add_key_value(pdf, "Status", "Delivered")
    _add_key_value(pdf, "Delivered At", _fmt_dt(delivered_event.created_at))
    _add_key_value(pdf, "Receiver Address", shipment.receiver_address)
    _add_key_value(pdf, "City", shipment.city or "N/A")
    _add_key_value(
        pdf,
        "Customer",
        f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
    )
    _add_key_value(
        pdf,
        "Courier",
        f"{courier.first_name} {courier.last_name}" if courier else "Unassigned",
    )

    if delivered_event.location_description:
        _add_key_value(pdf, "Delivery Location", delivered_event.location_description)
    if delivered_event.notes:
        _add_key_value(pdf, "Notes", delivered_event.notes)
    if delivered_event.proof_url:
        _add_key_value(pdf, "Proof", delivered_event.proof_url)

    return _output_pdf(pdf)
