import streamlit as st

# Standalone CCR Loop Debug Tool

def run_precise_ccr_loop(C, M, Q, T, F, N, S, R, q_value=62.50, tolerance=0.005, max_iterations=1000):
    """
    Inputs:
    C = Total Cash Down (incl. lease cash if applied)
    M = Taxable Fees (Doc + Acq)
    Q = Non-taxable LTR Fee
    T = Tax Rate (e.g. 0.0725)
    F = Money Factor
    N = Term in Months
    S = MSRP / Cap Cost
    R = Residual Value
    """

    min_ccr = 0.0
    max_ccr = S - R
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        ccr_guess = (min_ccr + max_ccr) / 2

        cap_cost = S + M
        adj_cap_cost = cap_cost - ccr_guess

        depreciation = (adj_cap_cost - R) / N
        rent_charge = (adj_cap_cost + R) * F

        base_payment = depreciation + rent_charge
        base_payment_rounded = round(base_payment, 2)

        monthly_tax = round(base_payment_rounded * T, 2)
        ltr_tax = round(q_value * T, 2)

        first_payment = round(base_payment_rounded + monthly_tax + q_value + ltr_tax, 2)
        ccr_tax = round(ccr_guess * T, 2)

        total = round(ccr_guess + ccr_tax + first_payment, 2)

        if abs(total - C) <= tolerance:
            return {
                "CCR": round(ccr_guess, 2),
                "CCR_Tax": ccr_tax,
                "First_Payment": first_payment,
                "Iterations": iteration,
                "Total": total
            }

        if total > C:
            max_ccr = ccr_gu
