import streamlit as st

# Hybrid CCR Loop: Start linear then switch to binary when close

def run_hybrid_ccr_loop(C, M, Q, T, F, N, S, R, q_value=62.50, tolerance=0.005, linear_step=100.0, max_iterations=1000):
    cap_cost = S + M
    iteration = 0
    history = []

    # Linear Phase
    ccr_guess = C
    while ccr_guess >= 0:
        iteration += 1
        adj_cap_cost = cap_cost - ccr_guess

        depreciation = (adj_cap_cost - R) / N
        rent_charge = (adj_cap_cost + R) * F
        base_payment = depreciation + rent_charge
        monthly_tax = round(base_payment * T, 2)
        ltr_tax = round(q_value * T, 2)
        first_payment = round(base_payment + monthly_tax + Q + ltr_tax, 2)
        ccr_tax = round(ccr_guess * T, 2)
        total = round(ccr_guess + ccr_tax + first_payment, 2)

        history.append({"Iteration": iteration, "CCR_Guess": round(ccr_guess, 2), "CCR_Tax": ccr_tax, "First_Payment": first_payment, "Total": total})

        if abs(total - C) <= tolerance:
            return {"CCR": round(ccr_guess, 2), "CCR_Tax": ccr_tax, "First_Payment": first_payment, "Iterations": iteration, "Total": total, "History": history}

        # Stop when we're within a small range to allow binary both directions
        if abs(total - C) < (linear_step * 1.5):
            break

        ccr_guess -= linear_step

    # Binary Phase
    min_ccr = ccr_guess
    max_ccr = min(C, ccr_guess + linear_step * 2)
    while iteration < max_iterations:
        iteration += 1
        ccr_guess = (min_ccr + max_ccr) / 2
        adj_cap_cost = cap_cost - ccr_guess

        depreciation = (adj_cap_cost - R) / N
        rent_charge = (adj_cap_cost + R) * F
        base_payment = depreciation + rent_charge
        monthly_tax = round(base_payment * T, 2)
        ltr_tax = round(q_value * T, 2)
        first_payment = round(base_payment + monthly_tax + Q + ltr_tax, 2)
        ccr_tax = round(ccr_guess * T, 2)
        total = round(ccr_guess + ccr_tax + first_payment, 2)

        history.append({"Iteration": iteration, "CCR_Guess": round(ccr_guess, 2), "CCR_Tax": ccr_tax, "First_Payment": first_payment, "Total": total})

        if abs(total - C) <= tolerance:
            return {"CCR": round(ccr_guess, 2), "CCR_Tax": ccr_tax, "First_Payment": first_payment, "Iterations": iteration, "Total": total, "History": history}

        if total > C:
            max_ccr = ccr_guess
        else:
            min_ccr = ccr_guess

    return {"CCR": None, "CCR_Tax": None, "First_Payment": None, "Iterations": iteration, "Total": None, "History": history}

def main():
    st.title("CCR Hybrid Loop Debug Tool")

    C = st.number_input("Down Payment (C)", value=1000.00)
    M = st.number_input("Taxable Fees (M: Doc + Acq)", value=900.00)
    Q = st.number_input("LTR Fee (Q)", value=62.50)
    T = st.number_input("Tax Rate (T)", value=0.0725, format="%.4f")
    F = st.number_input("Money Factor (F)", value=0.00293, format="%.6f")
    N = st.number_input("Term (N)", value=36)
    S = st.number_input("Cap Cost / MSRP (S)", value=25040.00)
    R = st.number_input("Residual (R)", value=16276.00)

    if st.button("Run Hybrid Loop"):
        st.write(f"Running with Down Payment = ${C:.2f}")
        result = run_hybrid_ccr_loop(C, M, Q, T, F, N, S, R)

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
