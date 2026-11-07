#!/usr/bin/env python3
"""Calculate a conservative planning estimate, not a provider spending control."""
import argparse,json,sys
from decimal import Decimal,InvalidOperation

def money(value):
    try:
        v=Decimal(str(value))
        if not v.is_finite() or v<0:raise ValueError()
        return v
    except (InvalidOperation,ValueError):raise ValueError('All budget values must be nonnegative finite numbers') from None

def estimate(data):
    if not isinstance(data,dict) or not isinstance(data.get('services'),list) or not data['services']:raise ValueError('At least one service estimate required')
    ceiling=money(data.get('ceiling_cad'));fx=money(data.get('cad_per_usd'));tax=money(data.get('tax_fraction'));reserve=money(data.get('reserve_cad'))
    if not ceiling or not fx or tax>1:raise ValueError('Ceiling and exchange rate must be positive; tax_fraction must be at most 1')
    total=Decimal('0');details=[]
    for service in data['services']:
        if not isinstance(service,dict) or not isinstance(service.get('name'),str) or not service['name'].strip():raise ValueError('Every service needs a name')
        currency=service.get('currency');cost=money(service.get('monthly'))
        if currency not in ('CAD','USD'):raise ValueError('Service currency must be CAD or USD')
        converted=cost*(fx if currency=='USD' else Decimal('1'));total+=converted;details.append({'name':service['name'],'estimated_cad_before_tax':str(converted.quantize(Decimal('0.01')))})
    # Apply selected tax conservatively to all services; actual tax may differ.
    taxed=total*(Decimal('1')+tax);planned=taxed+reserve
    return {'services':details,'total_with_assumed_tax_and_reserve_cad':str(planned.quantize(Decimal('0.01'))),'within_ceiling_estimate':planned<=ceiling,'note':'Planning estimate only. Inputs are user-supplied assumptions, not a current quote, measured usage, invoice, or hard spending limit. Include existing Gemini subscription if it counts, provider fees, taxes, exchange spreads and all variable usage. Actual totals can exceed this.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');a=p.parse_args()
    with open(a.config,encoding='utf-8') as f:data=json.load(f)
    print(json.dumps(estimate(data),indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,json.JSONDecodeError) as e:print(f'Error: {e}',file=sys.stderr);sys.exit(1)
