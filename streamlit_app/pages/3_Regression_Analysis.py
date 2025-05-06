# ======================== Import Required Libraries ========================
import streamlit as st
import pandas as pd
import plotly.express as px

# Custom modules for data and model handling
from scripts.data_loader import load_data
from scripts.regression import (
    prepare_regression_data,
    fit_ols_model,
    get_regression_diagnostics,
    detect_residual_outliers
)
from scripts.visualizations import (
    plot_residuals_vs_fitted,
    plot_residual_distribution,
    plot_qq,
    plot_residual_boxplot
)

# ======================== Page Configuration ========================
st.set_page_config(layout="wide")
st.title("📈 PM2.5 Regression Analysis")
st.markdown("Explore relationships between PM2.5 levels and geographic factors.")
st.markdown("A linear regression model was fitted to analyze the impact of various factors on PM2.5 levels.")
st.markdown("The model I fit was based on the following features: `Dim1` (settlement type) and `Location` (country). The target variable is `FactValueNumeric` (PM2.5 levels).")
st.markdown("The model summary and diagnostic plots are displayed below, along with an analysis of potential outliers in the residuals.")
st.markdown("This model performed much better than a model using `Dim1` and `ParentLocation` (region) as categorical variables")

# ======================== Load Cleaned Data ========================
df = load_data()

# ======================== Sidebar: Model Settings ========================
st.sidebar.header("Model Settings")

# Define target variable and categorical features
target_col = 'FactValueNumeric'
categorical_cols = ['Dim1', 'Location']

# ======================== Fit Regression Model ========================
# taken from notebooks/Regression_Analysis.ipynb

# Preprocess the Armenian data
# Preprocess the data (dummy encoding, etc.)
X, y = prepare_regression_data(df, target_col, categorical_cols)

# Fit an OLS regression model
model = fit_ols_model(X, y)

# Retrieve diagnostics: residuals, fitted values, etc.
diagnostics = get_regression_diagnostics(model)

# ======================== Create Tabs for Sections ========================
tab1, tab2, tab3 = st.tabs(["Model Summary", "Diagnostic Plots", "Residual Analysis"])

# ======================== TAB 1: Model Summary ========================
with tab1:
    st.header("Regression Model Summary")

    R_squared = model.rsquared
    R_squared_adj = model.rsquared_adj
    AIC = model.aic

    # ---- Display key performance metrics ----
    st.subheader("Model Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("R-squared", f"{R_squared:3f}", "Explained variance")
    with col2:
        st.metric("Adjusted R-squared", f"{R_squared_adj:3f}", "Adjusted for predictors")
    with col3:
        st.metric("AIC", f"{AIC:4g}", "Model quality indicator")

    # ---- Display full statsmodels summary ----
    st.subheader("Detailed Coefficients Analysis")
    with st.expander("Show Full Regression Results"):
        st.text(model.summary())

    # ---- Interpretation in plain English ----
    st.markdown("""
    **Key Coefficient Interpretation:**
    - Baseline: Afghanistan (omitted category) at 59.62 µg/m³
    - Example Location Impacts:
      - ⬇️ Armenia: 17.28 µg/m³ lower than Africa
      - ⬇️ Italy: -40.61 µg/m³ lower
      - ⬆️ Iran: -26.72 µg/m³ higher
    - Settlement Types:
      - Rural areas: 3.59  µg/m³ lower than baseline
      - Urban areas: 0.93 µg/m³ lower
    - Not all Coefficients are significant (p-values < 0.05):
        Cameroon        0.113844
        Kuwait          0.819707
        Qatar           0.756235
        Saudi Arabia    0.568200
        Tajikistan      0.396560
    """)

# ======================== TAB 2: Diagnostic Plots ========================
with tab2:
    st.header("Model Diagnostic Plots")

    # ---- Layout: 2x2 Diagnostic Grid ----
    col1, col2 = st.columns(2)

    # Residuals vs Fitted
    with col1:
        st.plotly_chart(
            plot_residuals_vs_fitted(diagnostics['fitted_values'], diagnostics['residuals']),
            use_container_width=True
        )
        # Boxplot of residuals
        st.plotly_chart(
            plot_residual_boxplot(diagnostics['residuals']),
            use_container_width=True
        )

    # Distribution and QQ Plot
    with col2:
        # Residual distribution histogram
        st.plotly_chart(
            plot_residual_distribution(diagnostics['residuals']),
            use_container_width=True
        )
        # QQ plot (normality check)
        st.pyplot(plot_qq(diagnostics['residuals']))

# ======================== TAB 3: Residual Outliers ========================
with tab3:
    st.header("Residual Outlier Analysis")

    # Detect extreme residuals using custom logic
    outliers = detect_residual_outliers(diagnostics['residuals'])

    st.metric("Potential Outliers Detected", len(outliers))

    # ---- Display results only if outliers exist ----
    if not outliers.empty:
        col1, col2 = st.columns(2)

        # ---- Scatter plot of outlier residuals ----
        with col1:
            st.subheader("Outlier Distribution")
            outliers_reset = outliers.reset_index()
            fig = px.scatter(
                outliers_reset,
                x='index',
                y='Residuals',
                color='Residuals',
                labels={'index': 'Observation Index'},
                title='Outlier Residual Values',
                color_continuous_scale='rdylbu_r'
            )
            st.plotly_chart(fig, use_container_width=True)

        # ---- Table of observations with largest residuals ----
        with col2:
            st.subheader("Outlier Data Points")
            st.dataframe(
                df.loc[outliers.index]
                  .join(outliers)
                  .sort_values('Residuals', ascending=False)
                  .rename(columns={'Residuals': 'Residual Value'}),
                use_container_width=True,
                height=400
            )
    else:
        st.success("No significant outliers detected in residuals")

# ======================== Sidebar: Model Interpretation ========================
st.sidebar.header("Model Interpretation")
st.sidebar.markdown("""
**Key Insights:**
1. **Regional Variations Matter Most:**
   - Americas & Western Pacific have significantly cleaner air
   - Eastern Mediterranean shows elevated PM2.5 levels

2. **Urban-Rural Gradient:**
   - Rural areas show lower PM2.5 than urban baseline
   - Most settlement types have better air than reference

3. **Model Limitations:**
   - Explains 30% of variance (R² = 0.301)
   - Residual autocorrelation (DW = 0.58)
   - Non-normal residuals (JB p < 0.001)

**Actionable Insights:**
- Focus on Eastern Mediterranean for mitigation
- Investigate why urban areas retain more pollution
- Consider additional predictors for better model fit
""")