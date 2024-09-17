from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import numexpr as ne
import re
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

class FormulaInput(BaseModel):
    varName: str
    varType: str  # 'number', 'string', 'currency', 'percentage'

class Formula(BaseModel):
    outputVar: str
    expression: str
    inputs: List[FormulaInput]

class RequestBody(BaseModel):
    data: List[Dict[str, Any]]
    formulas: List[Formula]

def clean_numeric(value: str) -> float:
    """
    Clean and convert string values to float, handling currency and percentage formats.
    """
    if isinstance(value, str):
        if 'USD' in value:
            value = re.sub(r'[^\d.]', '', value)
        elif '%' in value:
            value = re.sub(r'[^\d.]', '', value)
        else:
            value = re.sub(r'[^\d.]', '', value)
    elif isinstance(value, (int, float)):  # Handle already numeric values
        return float(value)
    else:
        logging.error(f"Unexpected type for value: {value}")
        raise HTTPException(status_code=400, detail=f"Unexpected type for value: {value}")

    try:
        return float(value)
    except ValueError:
        logging.error(f"Invalid numeric value: {value}")
        raise HTTPException(status_code=400, detail=f"Invalid numeric value: {value}")

def evaluate_expression(expression: str, data_row: Dict[str, Any]) -> Any:
    try:
        cleaned_row = {k: clean_numeric(v) for k, v in data_row.items() if v is not None}
        logging.debug(f"Evaluating expression: {expression} with data: {cleaned_row}")
        result = ne.evaluate(expression, local_dict=cleaned_row)
        return result.item()  # Convert numpy scalar to Python scalar
    except (ValueError, TypeError, NameError) as e:
        logging.error(f"Error evaluating expression: {expression}, error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error evaluating expression: {str(e)}")

@app.post("/api/execute-formula")
async def execute_formula(request_body: RequestBody):
    data = request_body.data
    formulas = request_body.formulas

    results = {}
    for formula in formulas:
        output_var = formula.outputVar
        expression = formula.expression
        inputs = {input_.varName: None for input_ in formula.inputs}

        formula_results = []
        for row in data:
            local_dict = {**row, **inputs}
            try:
                result = evaluate_expression(expression, local_dict)
                formula_results.append(result)
            except HTTPException as e:
                logging.error(f"Failed to evaluate expression for row: {row}. Error: {e.detail}")
                # Instead of continuing, you might want to return a response immediately
                return {"results": results, "status": "error", "message": f"Failed to evaluate expression for row: {row}. Error: {e.detail}"}

        results[output_var] = formula_results

    return {"results": results, "status": "success", "message": "The formulas were executed successfully."}
