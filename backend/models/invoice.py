from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    bill_type = Column(String, nullable=False)  # "NORMAL_BILL" or "GST_INVOICE"
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(String, nullable=True)
    invoice_date = Column(String, nullable=False)  # formatted date, e.g., "2026-07-09"
    apply_gst = Column(Boolean, default=False, nullable=False)
    gst_percent = Column(Float, default=0.0, nullable=False)
    tax_inclusive = Column(Boolean, default=False, nullable=False)
    external_fare = Column(Float, default=0.0, nullable=False)
    subtotal = Column(Float, nullable=False)
    taxable_value = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Cascade deletion so deleting an invoice automatically deletes its items
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    scrap_type = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
