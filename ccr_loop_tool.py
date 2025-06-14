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

    history = []

    while iteration < max_iterations:
        iteration += 1
        ccr_guess = (min_ccr + max_ccr) / 2

        cap_cost = S + M
        adj_cap_cost = cap_cost - ccr_guess

        depreciation = (adj_cap_cost - R) / N
        rent_charge = (adj_cap_cost + R) * F

        base_payment = depreciation + rent_charge
        monthly_tax = round(base_payment * T, 2)  # Avoid pre-rounding
        ltr_tax = round(q_value * T, 2)

        first_payment = round(base_payment + monthly_tax + Q + ltr_tax, 2)
        ccr_tax = round(ccr_guess * T, 2)

        total = round(ccr_guess + ccr_tax + first_payment, 2)

        history.append({
            "Iteration": iteration,
            "CCR_Guess": round(ccr_guess, 2),
            "CCR_Tax": ccr_tax,
            "First_Payment": first_payment,
            "Total": total
        })

        if abs(total - C) <= tolerance:
            return {
                "CCR": round(ccr_guess, 2),
                "CCR_Tax": ccr_tax,
                "First_Payment": first_payment,
                "Iterations": iteration,
                "Total": total,
                "History": history
            }

        if total > C:
            max_ccr = ccr_guess
        else:
            min_ccr = ccr_guess

    return {
        "CCR": None,
        "CCR_Tax": None,
        "First_Payment": None,
        "Iterations": iteration,
        "Total": None,
        "History": history
    }


def main():
    st.title("CCR Loop Debug Tool")

    C = st.number_input("Down Payment (C)", value=1000.00)
    M = st.number_input("Taxable Fees (M: Doc + Acq)", value=900.00)
    Q = st.number_input("LTR Fee (Q)", value=62.50)
    T = st.number_input("Tax Rate (T)", value=0.0725, format="%.4f")
    F = st.number_input("Money Factor (F)", value=0.00293, format="%.6f")
    N = st.number_input("Term (N)", value=36)
    S = st.number_input("Cap Cost / MSRP (S)", value=25040.00)
    R = st.number_input("Residual (R)", value=16276.00)

    if st.button("Run Loop"):
        result = run_precise_ccr_loop(C, M, Q, T, F, N, S, R)

        if result["CCR"] is not None:
            st.success("Loop completed!")
            st.write(f"**CCR:** ${result['CCR']:.2f}")
            st.write(f"**CCR Tax:** ${result['CCR_Tax']:.2f}")
            st.write(f"**First Payment:** ${result['First_Payment']:.2f}")
            st.write(f"**Iterations:** {result['Iterations']}")
            st.write(f"**Total (Matched):** ${result['Total']:.2f}")

            with st.expander("🔍 Show Iteration History"):
                for row in result["History"]:
                    st.write(
                        f"Iteration {row['Iteration']:>2}: "
                        f"CCR = ${row['CCR_Guess']:.2f}, "
                        f"CCR Tax = ${row['CCR_Tax']:.2f}, "
                        f"First Payment = ${row['First_Payment']:.2f}, "
                        f"Total = ${row['Total']:.2f}"
                    )
        else:
            st.error("Loop failed to converge within max iterations.")


if __name__ == "__main__":
    main()
