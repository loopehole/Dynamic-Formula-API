from pydantic import BaseModel
from typing import List

class DataItem(BaseModel):
    id: int
    product: str
    unitPrice: str  # Or use float if you will convert to numbers later
    quantity: int
    discount: str  # Or use float if you will convert to numbers later

class FormulaInput(BaseModel):
    varName: str
    varType: str  # 'number', 'string', 'currency', 'percentage'

class Formula(BaseModel):
    outputVar: str
    expression: str
    inputs: List[FormulaInput]

class FormulaPayload(BaseModel):
    data: List[DataItem]
    formulas: List[Formula]
