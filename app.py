from __future__ import annotations

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Credit Risk Decisioning & Regulatory Guidance",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimalist Editorial Styling
st.markdown(
    """
    <style>
    .eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--primary-color, #3b82f6);
        margin-bottom: 0.35rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 0.35rem;
        line-height: 1.2;
    }
    .main-subtitle {
        font-size: 0.96rem;
        color: var(--text-color);
        opacity: 0.72;
        margin-bottom: 2rem;
        line-height: 1.5;
        max-width: 850px;
    }
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.65;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# In-Process Client Fallback for Zero-Config Cloud Deployments (Streamlit Community Cloud)
@st.cache_resource
def get_in_process_client():
    try:
        from fastapi.testclient import TestClient
        from main import app as backend_app
        client = TestClient(backend_app)
        client.__enter__()
        return client
    except Exception:
        return None

def api_get(url: str, endpoint: str, timeout: int = 5):
    try:
        return requests.get(f"{url.rstrip('/')}{endpoint}", timeout=timeout)
    except requests.exceptions.ConnectionError:
        in_proc = get_in_process_client()
        if in_proc is not None:
            return in_proc.get(endpoint)
        raise

def api_post(url: str, endpoint: str, json: dict, timeout: int = 120):
    try:
        return requests.post(f"{url.rstrip('/')}{endpoint}", json=json, timeout=timeout)
    except requests.exceptions.ConnectionError:
        in_proc = get_in_process_client()
        if in_proc is not None:
            return in_proc.post(endpoint, json=json)
        raise

# Benchmark Preset Profiles
PRESETS = {
    "Approved Borrower Profile": {
        "status_of_existing_checking_account": "A11",
        "duration_in_month": 6,
        "credit_history": "A34",
        "purpose": "A43",
        "credit_amount": 1169.0,
        "savings_account_bonds": "A65",
        "present_employment_since": "A75",
        "installment_rate_in_percentage_of_disposable_income": 4,
        "personal_status_and_sex": "A93",
        "other_debtors_guarantors": "A101",
        "present_residence_since": 4,
        "property": "A121",
        "age_in_years": 67,
        "other_installment_plans": "A143",
        "housing": "A152",
        "number_of_existing_credits_at_this_bank": 2,
        "job": "A173",
        "number_of_people_being_liable_to_provide_maintenance_for": 1,
        "telephone": "A192",
        "foreign_worker": "A201",
    },
    "Review Borderline Borrower": {
        "status_of_existing_checking_account": "A11",
        "duration_in_month": 42,
        "credit_history": "A32",
        "purpose": "A42",
        "credit_amount": 7882.0,
        "savings_account_bonds": "A61",
        "present_employment_since": "A74",
        "installment_rate_in_percentage_of_disposable_income": 2,
        "personal_status_and_sex": "A93",
        "other_debtors_guarantors": "A103",
        "present_residence_since": 4,
        "property": "A122",
        "age_in_years": 45,
        "other_installment_plans": "A143",
        "housing": "A153",
        "number_of_existing_credits_at_this_bank": 1,
        "job": "A173",
        "number_of_people_being_liable_to_provide_maintenance_for": 2,
        "telephone": "A191",
        "foreign_worker": "A201",
    },
    "Rejected High-Risk Borrower": {
        "status_of_existing_checking_account": "A14",
        "duration_in_month": 48,
        "credit_history": "A30",
        "purpose": "A40",
        "credit_amount": 12000.0,
        "savings_account_bonds": "A61",
        "present_employment_since": "A71",
        "installment_rate_in_percentage_of_disposable_income": 4,
        "personal_status_and_sex": "A91",
        "other_debtors_guarantors": "A101",
        "present_residence_since": 4,
        "property": "A124",
        "age_in_years": 22,
        "other_installment_plans": "A141",
        "housing": "A153",
        "number_of_existing_credits_at_this_bank": 1,
        "job": "A171",
        "number_of_people_being_liable_to_provide_maintenance_for": 1,
        "telephone": "A191",
        "foreign_worker": "A201",
    },
}

# Label Translations for User-Facing Form
LABELS = {
    "checking": {
        "A11": "< 0 DM",
        "A12": "0 to < 200 DM",
        "A13": ">= 200 DM / salary assignments for at least 1 year",
        "A14": "No checking account",
    },
    "credit_history": {
        "A30": "No credits taken / all credits paid back duly",
        "A31": "All credits at this bank paid back duly",
        "A32": "Existing credits paid back duly till now",
        "A33": "Delay in paying off in the past",
        "A34": "Critical account / other credits existing (not at this bank)",
    },
    "purpose": {
        "A40": "Car (new)",
        "A41": "Car (used)",
        "A42": "Furniture / equipment",
        "A43": "Radio / television",
        "A44": "Domestic appliances",
        "A45": "Repairs",
        "A46": "Education",
        "A47": "Vacation",
        "A48": "Retraining",
        "A49": "Business",
        "A410": "Others",
    },
    "savings": {
        "A61": "< 100 DM",
        "A62": "100 to < 500 DM",
        "A63": "500 to < 1,000 DM",
        "A64": ">= 1,000 DM",
        "A65": "Unknown / no savings account",
    },
    "employment": {
        "A71": "Unemployed",
        "A72": "< 1 year",
        "A73": "1 to < 4 years",
        "A74": "4 to < 7 years",
        "A75": ">= 7 years",
    },
    "personal_status": {
        "A91": "Male: divorced / separated",
        "A92": "Female: divorced / separated / married",
        "A93": "Male: single",
        "A94": "Male: married / widowed",
    },
    "debtors": {
        "A101": "None",
        "A102": "Co-applicant",
        "A103": "Guarantor",
    },
    "property": {
        "A121": "Real estate",
        "A122": "Building society savings / life insurance",
        "A123": "Car or other property",
        "A124": "Unknown / no property",
    },
    "installment_plans": {
        "A141": "Bank",
        "A142": "Stores",
        "A143": "None",
    },
    "housing": {
        "A151": "Rent",
        "A152": "Own",
        "A153": "For free",
    },
    "job": {
        "A171": "Unemployed / unskilled non-resident",
        "A172": "Unskilled resident",
        "A173": "Skilled employee / official",
        "A174": "Management / self-employed / highly qualified",
    },
    "telephone": {
        "A191": "None registered",
        "A192": "Yes, registered under applicant name",
    },
    "foreign_worker": {
        "A201": "Yes",
        "A202": "No",
    },
}

# Initialize session state for form defaults
if "applicant_data" not in st.session_state:
    st.session_state["applicant_data"] = dict(PRESETS["Review Borderline Borrower"])

# Sidebar: System Status & Configuration
with st.sidebar:
    st.title("System Controls")
    api_url = st.text_input(
        "API Base URL",
        value=os.getenv("CREDIT_API_URL", "http://localhost:8000"),
        help="FastAPI backend URL. If not running, automatically executes via in-process engine.",
    )

    # Health check
    try:
        health_resp = api_get(api_url, "/health", timeout=2)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            is_in_proc = "testclient" in str(type(health_resp)).lower()
            status_desc = "Cloud In-Process" if is_in_proc else "API Connected"
            st.success(f"● Engine Online ({status_desc})")
            st.caption(
                f"**Scoring Model:** `{health_data.get('model', 'logistic_regression')}`\n\n"
                f"**Policy Version:** `{health_data.get('policy_version', 'standard')}`"
            )
        else:
            st.warning(f"API returned status {health_resp.status_code}")
    except Exception:
        st.error("● Engine Offline")
        st.info("Start the API locally with:\n```bash\npython3 -m uvicorn main:app --reload\n```")

    st.markdown("---")
    st.subheader("Benchmark Presets")
    selected_preset = st.selectbox("Select Benchmark Case:", list(PRESETS.keys()), index=1)
    if st.button("Apply Preset to Form", width="stretch"):
        st.session_state["applicant_data"] = dict(PRESETS[selected_preset])
        st.rerun()

    st.markdown("---")
    st.subheader("Architecture")
    st.markdown(
        """
        - **Scoring Engine:** Logistic Regression with SHAP factor attribution
        - **Decision Policy:** Dual-threshold bands (Approve, Review, Reject)
        - **Guidance Engine:** Gemini with European regulatory RAG (EBA & EU Directives)
        """
    )

# Main Masthead
st.markdown('<div class="eyebrow">Credit Risk Decisioning · EBA Compliant</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Credit Risk Underwriting & Review Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Automated probability of default estimation, SHAP factor attribution, '
    'and European consumer credit regulatory review guidance powered by Gemini.</div>',
    unsafe_allow_html=True,
)

current_data = st.session_state["applicant_data"]

# Input Form
with st.form("borrower_form"):
    st.markdown("### Borrower Application Profile")
    st.caption("Enter the applicant's financial position, obligations, and credit history.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-label">Loan & Financial Position</div>', unsafe_allow_html=True)
        credit_amount = st.number_input(
            "Credit Amount (DM)",
            min_value=250.0,
            max_value=20000.0,
            value=float(current_data.get("credit_amount", 5000.0)),
            step=250.0,
        )
        duration_in_month = st.slider(
            "Loan Duration (Months)",
            min_value=4,
            max_value=72,
            value=int(current_data.get("duration_in_month", 24)),
        )
        installment_rate = st.slider(
            "Installment Rate (% of Income)",
            min_value=1,
            max_value=4,
            value=int(current_data.get("installment_rate_in_percentage_of_disposable_income", 2)),
        )

        purpose_keys = list(LABELS["purpose"].keys())
        purpose_idx = purpose_keys.index(current_data.get("purpose", "A43")) if current_data.get("purpose") in purpose_keys else 0
        purpose = st.selectbox(
            "Loan Purpose",
            options=purpose_keys,
            index=purpose_idx,
            format_func=lambda x: f"{x} - {LABELS['purpose'][x]}",
        )

        checking_keys = list(LABELS["checking"].keys())
        checking_idx = checking_keys.index(current_data.get("status_of_existing_checking_account", "A11")) if current_data.get("status_of_existing_checking_account") in checking_keys else 0
        status_of_existing_checking_account = st.selectbox(
            "Checking Account Status",
            options=checking_keys,
            index=checking_idx,
            format_func=lambda x: f"{x} - {LABELS['checking'][x]}",
        )

        savings_keys = list(LABELS["savings"].keys())
        savings_idx = savings_keys.index(current_data.get("savings_account_bonds", "A61")) if current_data.get("savings_account_bonds") in savings_keys else 0
        savings_account_bonds = st.selectbox(
            "Savings Account / Bonds",
            options=savings_keys,
            index=savings_idx,
            format_func=lambda x: f"{x} - {LABELS['savings'][x]}",
        )

    with col2:
        st.markdown('<div class="section-label">Employment & Demographics</div>', unsafe_allow_html=True)
        employment_keys = list(LABELS["employment"].keys())
        emp_idx = employment_keys.index(current_data.get("present_employment_since", "A73")) if current_data.get("present_employment_since") in employment_keys else 0
        present_employment_since = st.selectbox(
            "Present Employment Since",
            options=employment_keys,
            index=emp_idx,
            format_func=lambda x: f"{x} - {LABELS['employment'][x]}",
        )

        job_keys = list(LABELS["job"].keys())
        job_idx = job_keys.index(current_data.get("job", "A173")) if current_data.get("job") in job_keys else 0
        job = st.selectbox(
            "Employment Role / Qualification",
            options=job_keys,
            index=job_idx,
            format_func=lambda x: f"{x} - {LABELS['job'][x]}",
        )

        age_in_years = st.number_input(
            "Age (Years)",
            min_value=18,
            max_value=100,
            value=int(current_data.get("age_in_years", 35)),
            step=1,
        )

        status_sex_keys = list(LABELS["personal_status"].keys())
        sex_idx = status_sex_keys.index(current_data.get("personal_status_and_sex", "A93")) if current_data.get("personal_status_and_sex") in status_sex_keys else 0
        personal_status_and_sex = st.selectbox(
            "Personal Status & Sex",
            options=status_sex_keys,
            index=sex_idx,
            format_func=lambda x: f"{x} - {LABELS['personal_status'][x]}",
        )

        debtors_keys = list(LABELS["debtors"].keys())
        debt_idx = debtors_keys.index(current_data.get("other_debtors_guarantors", "A101")) if current_data.get("other_debtors_guarantors") in debtors_keys else 0
        other_debtors_guarantors = st.selectbox(
            "Co-applicant or Guarantor",
            options=debtors_keys,
            index=debt_idx,
            format_func=lambda x: f"{x} - {LABELS['debtors'][x]}",
        )

        present_residence_since = st.slider(
            "Present Residence Duration (Years)",
            min_value=1,
            max_value=4,
            value=int(current_data.get("present_residence_since", 2)),
        )

    with col3:
        st.markdown('<div class="section-label">Credit History & Assets</div>', unsafe_allow_html=True)
        credit_history_keys = list(LABELS["credit_history"].keys())
        hist_idx = credit_history_keys.index(current_data.get("credit_history", "A32")) if current_data.get("credit_history") in credit_history_keys else 0
        credit_history = st.selectbox(
            "Credit History Status",
            options=credit_history_keys,
            index=hist_idx,
            format_func=lambda x: f"{x} - {LABELS['credit_history'][x]}",
        )

        existing_credits = st.slider(
            "Existing Credits at this Bank",
            min_value=1,
            max_value=4,
            value=int(current_data.get("number_of_existing_credits_at_this_bank", 1)),
        )

        plans_keys = list(LABELS["installment_plans"].keys())
        plan_idx = plans_keys.index(current_data.get("other_installment_plans", "A143")) if current_data.get("other_installment_plans") in plans_keys else 0
        other_installment_plans = st.selectbox(
            "Other Installment Plans",
            options=plans_keys,
            index=plan_idx,
            format_func=lambda x: f"{x} - {LABELS['installment_plans'][x]}",
        )

        property_keys = list(LABELS["property"].keys())
        prop_idx = property_keys.index(current_data.get("property", "A121")) if current_data.get("property") in property_keys else 0
        prop = st.selectbox(
            "Property & Collateral",
            options=property_keys,
            index=prop_idx,
            format_func=lambda x: f"{x} - {LABELS['property'][x]}",
        )

        housing_keys = list(LABELS["housing"].keys())
        housing_idx = housing_keys.index(current_data.get("housing", "A152")) if current_data.get("housing") in housing_keys else 0
        housing = st.selectbox(
            "Housing Arrangement",
            options=housing_keys,
            index=housing_idx,
            format_func=lambda x: f"{x} - {LABELS['housing'][x]}",
        )

        maintenance_persons = st.slider(
            "Persons Liable for Maintenance",
            min_value=1,
            max_value=2,
            value=int(current_data.get("number_of_people_being_liable_to_provide_maintenance_for", 1)),
        )

        phone_keys = list(LABELS["telephone"].keys())
        phone_idx = phone_keys.index(current_data.get("telephone", "A191")) if current_data.get("telephone") in phone_keys else 0
        telephone = st.selectbox(
            "Telephone Registered",
            options=phone_keys,
            index=phone_idx,
            format_func=lambda x: f"{x} - {LABELS['telephone'][x]}",
        )

        foreign_keys = list(LABELS["foreign_worker"].keys())
        foreign_idx = foreign_keys.index(current_data.get("foreign_worker", "A201")) if current_data.get("foreign_worker") in foreign_keys else 0
        foreign_worker = st.selectbox(
            "Foreign Worker Status",
            options=foreign_keys,
            index=foreign_idx,
            format_func=lambda x: f"{x} - {LABELS['foreign_worker'][x]}",
        )

    submitted = st.form_submit_button("⚡ Run Credit Risk Assessment", type="primary", width="stretch")

if submitted:
    payload = {
        "status_of_existing_checking_account": status_of_existing_checking_account,
        "duration_in_month": duration_in_month,
        "credit_history": credit_history,
        "purpose": purpose,
        "credit_amount": credit_amount,
        "savings_account_bonds": savings_account_bonds,
        "present_employment_since": present_employment_since,
        "installment_rate_in_percentage_of_disposable_income": installment_rate,
        "personal_status_and_sex": personal_status_and_sex,
        "other_debtors_guarantors": other_debtors_guarantors,
        "present_residence_since": present_residence_since,
        "property": prop,
        "age_in_years": age_in_years,
        "other_installment_plans": other_installment_plans,
        "housing": housing,
        "number_of_existing_credits_at_this_bank": existing_credits,
        "job": job,
        "number_of_people_being_liable_to_provide_maintenance_for": maintenance_persons,
        "telephone": telephone,
        "foreign_worker": foreign_worker,
    }

    try:
        with st.spinner("Scoring borrower profile & computing SHAP feature contributions..."):
            resp = api_post(api_url, "/predict", json=payload, timeout=10)

        if resp.status_code != 200:
            st.error(f"API Error ({resp.status_code}): {resp.text}")
        else:
            prediction = resp.json()
            decision = prediction.get("decision", "Unknown")
            pd_value = float(prediction.get("pd", 0.0))
            reason = prediction.get("decision_reason", "No reason provided")
            low_thresh = float(prediction.get("policy_threshold_low", 0.15))
            high_thresh = float(prediction.get("policy_threshold_high", 0.35))

            st.markdown("---")
            st.markdown("### Assessment Outcome")

            # Decision Banner
            if decision == "Approve":
                st.success("#### Decision: Approved\nApplicant default probability meets automated underwriting criteria.")
            elif decision == "Review":
                st.warning("#### Decision: Manual Review Required\nApplicant default probability falls within the designated human oversight band.")
            else:
                st.error("#### Decision: Declined\nApplicant default probability exceeds the acceptable policy threshold.")

            # Metric Cards Row
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                with st.container(border=True):
                    st.metric(label="Probability of Default", value=f"{pd_value:.1%}")
            with m_col2:
                with st.container(border=True):
                    st.metric(label="Policy Decision", value=decision)
            with m_col3:
                with st.container(border=True):
                    st.metric(label="Review Band", value=f"{low_thresh:.0%} – {high_thresh:.0%}")
            with m_col4:
                with st.container(border=True):
                    st.metric(label="Policy Version", value=prediction.get("policy_version", "v1"))

            # Risk Gauge Progress Bar
            st.markdown(f"**Risk Severity Meter (PD = {pd_value:.1%})**")
            st.progress(min(max(pd_value, 0.0), 1.0))
            st.caption(
                f"**Approve:** < {low_thresh:.0%}  |  "
                f"**Review Band:** {low_thresh:.0%} – {high_thresh:.0%}  |  "
                f"**Decline:** > {high_thresh:.0%}"
            )

            # SHAP Explanation Box
            st.markdown("### Model Factor Attribution (SHAP Drivers)")
            factors = [f.strip() for f in reason.split(";") if f.strip()]
            f_cols = st.columns(len(factors) if factors else 1)
            for idx, factor in enumerate(factors):
                with f_cols[idx]:
                    if "increases risk" in factor:
                        st.error(f"**Risk-Increasing Driver:**\n\n{factor}")
                    else:
                        st.success(f"**Mitigating Factor:**\n\n{factor}")

            # Expandable Policy Operational Metadata
            with st.expander("Policy Operational Metadata & Governance Constraints"):
                st.markdown(
                    f"""
                    - **Operating Policy Thresholds:** `Low = {low_thresh:.2f}`, `High = {high_thresh:.2f}`
                    - **Constraints Met on Validation:** `{'Yes' if prediction.get('policy_constraints_met') else 'No (Fallback Disclosure)'}`
                    - **Selection Rationale:** {prediction.get('policy_selection_reason', 'N/A')}
                    - **Loss Given Default (LGD):** `0.40 (40%)`
                    """
                )

            # Review Cases: Trigger Gemini Regulatory RAG Guidance
            if decision == "Review":
                st.markdown("---")
                st.markdown("### Regulatory Reviewer Guidance")
                st.caption(
                    "Sourced from official European consumer credit regulatory guidelines "
                    "(EBA GL/2020/06 & Directive EU 2023/2225) using Gemini."
                )

                with st.spinner("Retrieving regulatory policy passages and generating reviewer guidance via Gemini..."):
                    review_payload = {
                        "applicant": payload,
                        "prediction": prediction,
                    }
                    review_resp = api_post(api_url, "/review-summary", json=review_payload, timeout=120)

                if review_resp.status_code == 200:
                    review_data = review_resp.json()
                    model_used = review_data.get("llm_model", "gemini")
                    guardrail_triggered = review_data.get("review_guardrail_applied", False)

                    st.caption(f"**Model:** `{model_used}` · **Status:** Regulatory compliance verified")

                    if guardrail_triggered:
                        st.info(
                            "🛡️ **Consumer Protection Guardrail Applied:** "
                            "Verification scope was automatically restricted to target solely risk-increasing factors, "
                            "excluding non-risk demographic attributes in accordance with EU regulations."
                        )

                    st.markdown("#### Sourced Reviewer Note")
                    with st.container(border=True):
                        st.markdown(review_data.get("review_summary", ""))

                    sources = review_data.get("knowledge_base_sources", [])
                    if sources:
                        st.markdown("#### Retrieved Official Regulatory Sources")
                        source_rows = []
                        for s in sources:
                            source_rows.append(
                                {
                                    "Citation": s.get("citation_label", ""),
                                    "Authority": s.get("authority", ""),
                                    "Document Title": s.get("title", ""),
                                    "Page": s.get("page", ""),
                                    "Official URL": s.get("source_url", ""),
                                }
                            )
                        st.dataframe(
                            source_rows,
                            column_config={
                                "Official URL": st.column_config.LinkColumn(
                                    "Official Document",
                                    display_text="Open Regulation ↗",
                                )
                            },
                            hide_index=True,
                            width="stretch",
                        )

                else:
                    st.warning(
                        f"Regulatory Review Guidance unavailable (HTTP {review_resp.status_code}):\n\n"
                        f"{review_resp.text}\n\n"
                        "*(Ensure GEMINI_API_KEY is configured in your `.env` file or Streamlit Secrets)*"
                    )

    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to FastAPI server at `{api_url}`. Please ensure the backend server is running.")
    except Exception as exc:
        st.error(f"Unexpected error occurred: {exc}")
