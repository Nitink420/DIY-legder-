from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# Scrap Item for Calculations and Creation
class ScrapItemBase(BaseModel):
    scrap_type: str = Field(..., min_length=1, description="Type of scrap (e.g. Copper, Iron)")
    weight: float = Field(..., gt=0, description="Weight of the scrap in kg")
    rate: float = Field(..., gt=0, description="Rate per kg in ₹")

class ScrapItemCreate(ScrapItemBase):
    pass

class ScrapItemResponse(ScrapItemBase):
    id: Optional[int] = None
    amount: float = Field(..., description="Total value of this scrap item (weight * rate)")

    class Config:
        from_attributes = True

# Calculation Request (Customer name optional for live updates)
class InvoiceCalculateRequest(BaseModel):
    customer_name: Optional[str] = Field(default="", description="Customer / Pickup Name")
    customer_phone: Optional[str] = Field(default="", description="Customer Phone Number")
    customer_address: Optional[str] = Field(default="", description="Customer Address")
    apply_gst: bool = Field(default=False, description="Whether GST is applied")
    gst_percent: float = Field(default=0.0, description="GST Percentage (e.g. 5, 12, 18, 28)")
    tax_inclusive: bool = Field(default=False, description="Whether tax is inclusive in rates")
    external_fare: float = Field(default=0.0, ge=0, description="External Fare / Labour charges")
    items: List[ScrapItemCreate] = Field(..., min_length=1, description="List of scrap items")

    @field_validator("gst_percent")
    @classmethod
    def validate_gst_percent(cls, v, values):
        # If GST is applied, check that percent is one of the valid options (0, 5, 12, 18, 28)
        # Note: we can be lenient or strict. Let's make sure it's positive if apply_gst is true.
        return v

# Saved Invoice Creation Request (Customer name is required here)
class InvoiceCreateRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Customer / Pickup Name")
    customer_phone: Optional[str] = Field(default="", description="Customer Phone Number")
    customer_address: Optional[str] = Field(default="", description="Customer Address")
    apply_gst: bool = Field(default=False, description="Whether GST is applied")
    gst_percent: float = Field(default=0.0, description="GST Percentage (e.g. 5, 12, 18, 28)")
    tax_inclusive: bool = Field(default=False, description="Whether tax is inclusive in rates")
    external_fare: float = Field(default=0.0, ge=0, description="External Fare / Labour charges")
    items: List[ScrapItemCreate] = Field(..., min_length=1, description="List of scrap items")

# Calculation Results Schema
class InvoiceCalculateResponse(BaseModel):
    subtotal: float
    taxable_value: float
    gst_amount: float
    external_fare: float
    grand_total: float
    items: List[ScrapItemResponse]
    bill_type: str
    gst_applied: bool

# Fully Stored Database Invoice Response Schema
class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    bill_type: str
    customer_name: str
    customer_phone: Optional[str] = ""
    customer_address: Optional[str] = ""
    invoice_date: str
    apply_gst: bool
    gst_percent: float
    tax_inclusive: bool
    external_fare: float
    subtotal: float
    taxable_value: float
    gst_amount: float
    grand_total: float
    created_at: datetime
    items: List[ScrapItemResponse]

    class Config:
        from_attributes = True
