from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models.invoice import Invoice, InvoiceItem
from backend.schemas.invoice import (
    InvoiceCalculateRequest,
    InvoiceCalculateResponse,
    InvoiceCreateRequest,
    InvoiceResponse
)

router = APIRouter()

# Helper function to perform calculations
def perform_calculation(apply_gst: bool, gst_percent: float, tax_inclusive: bool, external_fare: float, items):
    item_totals = []
    inclusive_total = 0.0
    
    # Calculate item-wise totals
    for item in items:
        item_total = item.weight * item.rate
        inclusive_total += item_total
        item_totals.append({
            "scrap_type": item.scrap_type,
            "weight": round(item.weight, 2),
            "rate": round(item.rate, 2),
            "amount": round(item_total, 2)
        })

    if not apply_gst:
        subtotal = inclusive_total
        taxable_value = subtotal
        gst_amount = 0.00
        grand_total = subtotal + external_fare
        bill_type = "NORMAL_BILL"
        gst_applied = False
        gst_percent = 0.0
        tax_inclusive = False
    else:
        gst_applied = True
        bill_type = "GST_INVOICE"
        if tax_inclusive:
            # Inclusive of tax logic
            # Entered rate includes GST
            subtotal = inclusive_total
            taxable_value = inclusive_total / (1 + (gst_percent / 100))
            gst_amount = inclusive_total - taxable_value
            grand_total = inclusive_total + external_fare
        else:
            # Exclusive of tax logic
            # Entered rate is exclusive of GST
            subtotal = inclusive_total
            taxable_value = subtotal
            gst_amount = taxable_value * (gst_percent / 100)
            grand_total = subtotal + gst_amount + external_fare

    return {
        "subtotal": round(subtotal, 2),
        "taxable_value": round(taxable_value, 2),
        "gst_amount": round(gst_amount, 2),
        "external_fare": round(external_fare, 2),
        "grand_total": round(grand_total, 2),
        "items": item_totals,
        "bill_type": bill_type,
        "gst_applied": gst_applied,
        "gst_percent": gst_percent if gst_applied else 0.0,
        "tax_inclusive": tax_inclusive if gst_applied else False
    }

@router.post("/calculate", response_model=InvoiceCalculateResponse)
def calculate_invoice(payload: InvoiceCalculateRequest):
    try:
        results = perform_calculation(
            apply_gst=payload.apply_gst,
            gst_percent=payload.gst_percent,
            tax_inclusive=payload.tax_inclusive,
            external_fare=payload.external_fare,
            items=payload.items
        )
        return InvoiceCalculateResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}"
        )

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreateRequest, db: Session = Depends(get_db)):
    try:
        # Calculate totals
        calc = perform_calculation(
            apply_gst=payload.apply_gst,
            gst_percent=payload.gst_percent,
            tax_inclusive=payload.tax_inclusive,
            external_fare=payload.external_fare,
            items=payload.items
        )

        current_year = datetime.now().year
        bill_type = calc["bill_type"]

        # Generate invoice number based on year and type
        # Format: SKV-GST-2026-0001 or SKV-BILL-2026-0001
        prefix = f"SKV-GST-{current_year}-" if bill_type == "GST_INVOICE" else f"SKV-BILL-{current_year}-"
        
        # Scan the database for invoice numbers matching this prefix to find the max suffix sequence
        existing_numbers = db.query(Invoice.invoice_number).filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).all()
        
        max_seq = 0
        for (inv_num,) in existing_numbers:
            try:
                parts = inv_num.split("-")
                seq = int(parts[-1])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
        
        next_seq = max_seq + 1
        invoice_number = f"{prefix}{next_seq:04d}"
        invoice_date = datetime.now().strftime("%Y-%m-%d")

        # Create Invoice Model instance
        db_invoice = Invoice(
            invoice_number=invoice_number,
            bill_type=bill_type,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            customer_address=payload.customer_address,
            invoice_date=invoice_date,
            apply_gst=calc["gst_applied"],
            gst_percent=calc["gst_percent"],
            tax_inclusive=calc["tax_inclusive"],
            external_fare=calc["external_fare"],
            subtotal=calc["subtotal"],
            taxable_value=calc["taxable_value"],
            gst_amount=calc["gst_amount"],
            grand_total=calc["grand_total"]
        )

        db.add(db_invoice)
        db.flush()  # Flushes to get db_invoice.id for foreign keys

        # Create Invoice Items
        for item in calc["items"]:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                scrap_type=item["scrap_type"],
                weight=item["weight"],
                rate=item["rate"],
                amount=item["amount"]
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create invoice: {str(e)}"
        )

@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(db: Session = Depends(get_db)):
    try:
        # Return all invoices, latest first
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
        return invoices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve invoices: {str(e)}"
        )

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice

@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_200_OK)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    try:
        db.delete(invoice)
        db.commit()
        return {"status": "success", "message": f"Invoice {invoice.invoice_number} deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete invoice: {str(e)}"
        )
