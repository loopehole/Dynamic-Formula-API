import ast
import re
from models import Formula, FormulaPayload
from utils import parse_currency, parse_percentage

def validate_formula(expression: str):
    allowed_chars = re.compile(r'^[0-9+\-*/(). ]+$')
    if not allowed_chars.match(expression):
        raise ValueError("Expression contains invalid characters")

    try:
        ast.parse(expression, mode='eval')
    except SyntaxError:
        raise ValueError("Expression has invalid syntax")

def determine_execution_order(formulas):
    # Build dependency graph
    dependencies = {}
    for formula in formulas:
        dependencies[formula.outputVar] = set(var.varName for var in formula.inputs)
    
    # Sort formulas based on dependencies
    sorted_formulas = []
    resolved = set()

    def resolve(formula_name):
        if formula_name in resolved:
            return
        for dep in dependencies.get(formula_name, []):
            if dep not in resolved:
                resolve(dep)
        sorted_formulas.append(formula_name)
        resolved.add(formula_name)

    for formula in formulas:
        resolve(formula.outputVar)
    return sorted_formulas

def evaluate_formula(payload: FormulaPayload):
    results = {}
    data = payload.data
    
    # Convert data fields to appropriate types
    for item in data:
        item.unitPrice = parse_currency(item.unitPrice)
        item.discount = parse_percentage(item.discount)
    
    # Build a dependency graph (this determines the execution order)
    execution_order = determine_execution_order(payload.formulas)
    
    for formula_name in execution_order:
        formula = next(f for f in payload.formulas if f.outputVar == formula_name)
        expression = formula.expression
        
        # Validate the formula
        validate_formula(expression)
        
        # Replace variables in the expression with actual values
        for var in formula.inputs:
            if var.varName in results:
                expression = expression.replace(var.varName, str(results[var.varName]))
            else:
                for item in data:
                    if hasattr(item, var.varName):
                        expression = expression.replace(var.varName, str(getattr(item, var.varName)))
        
        # Safely evaluate the expression
        results[formula.outputVar] = safe_eval(expression)
    
    return results

def safe_eval(expr: str):
    try:
        allowed_locals = {"__builtins__": {}}
        return eval(expr, {"__builtins__": {}}, allowed_locals)
    except ZeroDivisionError:
        raise ValueError("Division by zero error in expression")
    except Exception as e:
        raise ValueError(f"Invalid expression: {expr}. Error: {str(e)}")
