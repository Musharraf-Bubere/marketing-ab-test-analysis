"""
scripts/build_financial_model.py
--------------------------------
Phase 6: Business Impact & Commercial Decision Model.
Constructs a dynamic Excel financial model (dashboard/business_impact_model.xlsx)
using live formulas, an Inputs sheet, 2D sensitivity analysis, and scenario comparisons.
All assumptions are clearly labeled as HYPOTHETICAL.
Recalculates and caches formula values using Excel COM.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd


def build_excel_financial_model(output_path: str = "dashboard/business_impact_model.xlsx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()

    # Define color palette & styles
    font_title = Font(name="Calibri", size=16, bold=True, color="1F497D")
    font_section = Font(name="Calibri", size=13, bold=True, color="1F497D")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_regular = Font(name="Calibri", size=11)
    font_italic = Font(name="Calibri", size=10, italic=True, color="595959")
    font_alert = Font(name="Calibri", size=10, italic=True, color="C00000", bold=True)

    fill_navy = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    fill_slate = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    fill_light_blue = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    fill_green = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    fill_red = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="D9D9D9")
    double_bottom_side = Side(border_style="double", color="1F497D")
    thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    summary_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=double_bottom_side)

    # -------------------------------------------------------------
    # TAB 1: Inputs & Assumptions
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Inputs_Assumptions"
    ws1.views.sheetView[0].showGridLines = True

    ws1["A1"] = "Marketing Campaign A/B Test: Commercial Impact Model"
    ws1["A1"].font = font_title
    ws1["A2"] = "[HYPOTHETICAL ASSUMPTIONS - FOR PLANNING & SCENARIO EVALUATION ONLY]"
    ws1["A2"].font = font_alert

    ws1["A4"] = "1. Financial & Unit Economics Assumptions (User Inputs)"
    ws1["A4"].font = font_section

    headers1 = ["Parameter", "Base Case", "Unit", "Sensitivity Range / Notes"]
    for col_num, h in enumerate(headers1, 1):
        cell = ws1.cell(row=5, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center")

    params1 = [
        ("Gross Margin per Conversion", 40.0, "$ / order", "Sensitivity tested from $5 to $100"),
        ("Cost per Thousand Impressions (CPM)", 2.00, "$ / 1k impressions", "Sensitivity tested from $1 to $10"),
        ("Cost per Single Ad Impression", "='Inputs_Assumptions'!B7/1000", "$ / impression", "Derived formula (= CPM / 1,000)"),
    ]

    for row_idx, (param, val, unit, notes) in enumerate(params1, 6):
        ws1.cell(row=row_idx, column=1, value=param).font = font_bold
        c_val = ws1.cell(row=row_idx, column=2, value=val)
        c_val.font = font_bold
        c_val.fill = fill_light_blue
        if isinstance(val, (int, float)):
            c_val.number_format = "$#,##0.00"
        elif str(val).startswith("="):
            c_val.number_format = "$#,##0.0000"
        ws1.cell(row=row_idx, column=3, value=unit).font = font_regular
        ws1.cell(row=row_idx, column=4, value=notes).font = font_italic
        for c in range(1, 5):
            ws1.cell(row=row_idx, column=c).border = thin_border

    ws1["A10"] = "2. Empirical Experiment Metrics (from Executed A/B Test Data)"
    ws1["A10"].font = font_section

    headers2 = ["Experiment Metric", "Observed Value", "Unit", "Source / Derivation"]
    for col_num, h in enumerate(headers2, 1):
        cell = ws1.cell(row=11, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_slate
        cell.alignment = Alignment(horizontal="center", vertical="center")

    empirical_metrics = [
        ("Treatment Population (Ad Cohort)", 564577, "users", "Executed SQL / SQLite database"),
        ("Control Population (PSA Cohort)", 23524, "users", "Executed SQL / SQLite database"),
        ("Treatment Total Ad Impressions Served", 14014692, "impressions", "Sum of total_ads in Treatment cohort"),
        ("Control Baseline Conversion Rate", 0.017854, "rate", "420 conversions / 23,524 users (1.7854%)"),
        ("Treatment Observed Conversion Rate", 0.025547, "rate", "14,423 conversions / 564,577 users (2.5547%)"),
        ("Expected Baseline Conversions (Without Campaign)", "=ROUND(B12*B15, 0)", "conversions", "Formula: Treatment Users * Control CR"),
        ("Treatment Total Observed Conversions", 14423, "conversions", "Observed buyers in Treatment cohort"),
        ("Incremental Conversions (Point Estimate - Base Case)", "=B18-B17", "conversions", "Observed Treatment - Expected Baseline"),
        ("Incremental Conversions (Low - 95% CI Lower Bound)", 3360, "conversions", "564,577 users * 0.5951% pts lift (conservative bound)"),
        ("Incremental Conversions (High - 95% CI Upper Bound)", 5326, "conversions", "564,577 users * 0.9434% pts lift (optimistic bound)"),
    ]

    for row_idx, (metric, val, unit, src) in enumerate(empirical_metrics, 12):
        ws1.cell(row=row_idx, column=1, value=metric).font = font_regular
        c_val = ws1.cell(row=row_idx, column=2, value=val)
        c_val.font = font_bold
        if "rate" in unit:
            c_val.number_format = "0.0000%"
        else:
            c_val.number_format = "#,##0"
        ws1.cell(row=row_idx, column=3, value=unit).font = font_regular
        ws1.cell(row=row_idx, column=4, value=src).font = font_italic
        for c in range(1, 5):
            ws1.cell(row=row_idx, column=c).border = thin_border

    ws1["A24"] = "3. Frequency Capping Parameters (Cap at 100 Impressions)"
    ws1["A24"].font = font_section

    cap_metrics = [
        ("Users Exposed to > 100 Ads", 22054, "users", "Treatment users seeing > 100 ads"),
        ("Uncapped Impressions in 100+ Tier", 4058074, "impressions", "Current impressions served to 100+ tier"),
        ("Capped Impressions in 100+ Tier (Cap @ 100)", "=B25*100", "impressions", "Formula: 22,054 users * 100 ads max"),
        ("Impressions Saved via 100-Ad Cap", "=B26-B27", "impressions", "Reduction in impressions beyond the 100th ad"),
        ("Total Campaign Impressions with 100-Ad Cap", "=B14-B28", "impressions", "14,014,692 uncapped - 1,852,674 saved beyond 100th ad"),
        ("Incremental Conversions Generated in 100+ Tier", 1159, "conversions", "Current causal lift in 100+ tier (44.2% rel lift)"),
    ]

    for row_idx, (metric, val, unit, src) in enumerate(cap_metrics, 25):
        ws1.cell(row=row_idx, column=1, value=metric).font = font_regular
        c_val = ws1.cell(row=row_idx, column=2, value=val)
        c_val.font = font_bold
        c_val.number_format = "#,##0"
        ws1.cell(row=row_idx, column=3, value=unit).font = font_regular
        ws1.cell(row=row_idx, column=4, value=src).font = font_italic
        for c in range(1, 5):
            ws1.cell(row=row_idx, column=c).border = thin_border

    # -------------------------------------------------------------
    # TAB 2: Executive Summary & Break-Even
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Executive_Summary")
    ws2.views.sheetView[0].showGridLines = True

    ws2["A1"] = "Executive Campaign Performance & Break-Even Analysis"
    ws2["A1"].font = font_title
    ws2["A2"] = "[DYNAMIC FORMULAS DRIVEN BY INPUTS SHEET - HYPOTHETICAL ASSUMPTIONS]"
    ws2["A2"].font = font_alert

    ws2["A4"] = "1. Financial Performance Across Statistical Confidence Bounds"
    ws2["A4"].font = font_section

    headers_summary = ["Financial Metric", "Conservative (95% CI Low)", "Base Case (Point Estimate)", "Optimistic (95% CI High)", "Formula Derivation"]
    for col_num, h in enumerate(headers_summary, 1):
        cell = ws2.cell(row=5, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center")

    summary_rows = [
        ("Incremental Conversions", "='Inputs_Assumptions'!B20", "='Inputs_Assumptions'!B19", "='Inputs_Assumptions'!B21", "#,##0", "From statistical test (CI lower / point / CI upper)"),
        ("Gross Margin per Conversion", "='Inputs_Assumptions'!B6", "='Inputs_Assumptions'!B6", "='Inputs_Assumptions'!B6", "$#,##0.00", "Hypothetical user input ($40 base margin)"),
        ("Incremental Gross Profit", "=B6*B7", "=C6*C7", "=D6*D7", "$#,##0", "Incremental Conversions * Gross Margin per Conversion"),
        ("Total Ad Impressions Served", "='Inputs_Assumptions'!B14", "='Inputs_Assumptions'!B14", "='Inputs_Assumptions'!B14", "#,##0", "14,014,692 impressions (empirical)"),
        ("Cost per 1,000 Impressions (CPM)", "='Inputs_Assumptions'!B7", "='Inputs_Assumptions'!B7", "='Inputs_Assumptions'!B7", "$#,##0.00", "Hypothetical user input ($2.00 base)"),
        ("Total Campaign Media Spend", "=(B9/1000)*B10", "=(C9/1000)*C10", "=(D9/1000)*D10", "$#,##0", "(Total Impressions / 1,000) * CPM"),
        ("Net Incremental Profit", "=B8-B11", "=C8-C11", "=D8-D11", "$#,##0", "Incremental Gross Profit - Total Media Spend"),
        ("Margin-based Return on Ad Spend (ROAS)", "=B8/B11", "=C8/C11", "=D8/D11", "0.00x", "Incremental Gross Profit / Total Media Spend"),
        ("Cost per Incremental Conversion (CAC)", "=B11/B6", "=C11/C6", "=D11/D6", "$#,##0.00", "Total Media Spend / Incremental Conversions"),
    ]

    for row_idx, (label, f_low, f_base, f_high, num_fmt, desc) in enumerate(summary_rows, 6):
        ws2.cell(row=row_idx, column=1, value=label).font = font_bold if label in ["Net Incremental Profit", "Margin-based Return on Ad Spend (ROAS)"] else font_regular
        for col_idx, form in enumerate([f_low, f_base, f_high], 2):
            cell = ws2.cell(row=row_idx, column=col_idx, value=form)
            cell.font = font_bold if label in ["Net Incremental Profit", "Margin-based Return on Ad Spend (ROAS)"] else font_regular
            cell.number_format = num_fmt
            if label == "Net Incremental Profit":
                cell.fill = fill_green
        ws2.cell(row=row_idx, column=5, value=desc).font = font_italic
        for c in range(1, 6):
            ws2.cell(row=row_idx, column=c).border = summary_border if label == "Net Incremental Profit" else thin_border

    ws2["A17"] = "2. Explicit Break-Even Analysis"
    ws2["A17"].font = font_section

    headers_be = ["Break-Even Metric", "Conservative (95% CI Low)", "Base Case", "Optimistic (95% CI High)", "Business Interpretation"]
    for col_num, h in enumerate(headers_be, 1):
        cell = ws2.cell(row=18, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_slate
        cell.alignment = Alignment(horizontal="center", vertical="center")

    be_rows = [
        ("Break-Even CPM (Maximum viable CPM at $40 margin)", "=(B6*'Inputs_Assumptions'!B6)/('Inputs_Assumptions'!B14/1000)", "=(C6*'Inputs_Assumptions'!B6)/('Inputs_Assumptions'!B14/1000)", "=(D6*'Inputs_Assumptions'!B6)/('Inputs_Assumptions'!B14/1000)", "$#,##0.00", "If actual CPM exceeds this threshold, campaign is net-negative"),
        ("Break-Even Margin (Minimum required margin at $2.00 CPM)", "=B11/B6", "=C11/C6", "=D11/D6", "$#,##0.00", "If gross margin per order falls below this value, campaign loses money"),
    ]

    for row_idx, (label, f_low, f_base, f_high, num_fmt, desc) in enumerate(be_rows, 19):
        ws2.cell(row=row_idx, column=1, value=label).font = font_bold
        for col_idx, form in enumerate([f_low, f_base, f_high], 2):
            cell = ws2.cell(row=row_idx, column=col_idx, value=form)
            cell.font = font_bold
            cell.number_format = num_fmt
            cell.fill = fill_light_blue
        ws2.cell(row=row_idx, column=5, value=desc).font = font_italic
        for c in range(1, 6):
            ws2.cell(row=row_idx, column=c).border = thin_border

    # -------------------------------------------------------------
    # TAB 3: Sensitivity Matrix (2D: CPM vs Margin)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Sensitivity_Matrix")
    ws3.views.sheetView[0].showGridLines = True

    ws3["A1"] = "2D Sensitivity Matrix: Net Incremental Profit ($)"
    ws3["A1"].font = font_title
    ws3["A2"] = "[BASE CASE: 4,343 INCREMENTAL CONVERSIONS | 14,014,692 IMPRESSIONS - ALL FORMULAS LIVE]"
    ws3["A2"].font = font_alert

    cpms = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
    margins = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 75.0, 100.0]

    ws3["A4"] = "CPM \\ Margin"
    ws3["A4"].font = font_header
    ws3["A4"].fill = fill_navy
    ws3["A4"].alignment = Alignment(horizontal="center")

    for col_idx, m in enumerate(margins, 2):
        c = ws3.cell(row=4, column=col_idx, value=m)
        c.font = font_header
        c.fill = fill_navy
        c.number_format = "$#,##0"
        c.alignment = Alignment(horizontal="center")

    for row_idx, cpm in enumerate(cpms, 5):
        c_label = ws3.cell(row=row_idx, column=1, value=cpm)
        c_label.font = font_bold
        c_label.fill = fill_light_blue
        c_label.number_format = "$#,##0.00"
        c_label.alignment = Alignment(horizontal="center")

        for col_idx in range(2, len(margins) + 2):
            m_cell_ref = f"{get_column_letter(col_idx)}$4"
            cpm_cell_ref = f"$A{row_idx}"
            # Net Profit Formula: (Incremental Conversions * Margin) - ((Total Impressions / 1000) * CPM)
            formula = f"=('Inputs_Assumptions'!$B$19*{m_cell_ref})-(('Inputs_Assumptions'!$B$14/1000)*{cpm_cell_ref})"
            c_profit = ws3.cell(row=row_idx, column=col_idx, value=formula)
            c_profit.number_format = "$#,##0"
            c_profit.border = thin_border

    # -------------------------------------------------------------
    # TAB 4: Scenario Comparison (Uncapped vs Capped @ 100 Ads)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="Scenario_Comparison")
    ws4.views.sheetView[0].showGridLines = True

    ws4["A1"] = "Strategic Scenario Analysis: Uncapped vs. Frequency-Capped Rollout"
    ws4["A1"].font = font_title
    ws4["A2"] = "[CAP EVALUATED AT 100 IMPRESSIONS ACROSS 100%, 75%, AND 50% RETENTION ASSUMPTIONS]"
    ws4["A2"].font = font_alert

    headers_scen = [
        "Scenario Strategy",
        "Total Impressions",
        "Media Spend (@ $2 CPM)",
        "Incremental Conversions",
        "Incremental Gross Profit (@ $40 Margin)",
        "Net Incremental Profit",
        "Margin-based ROAS",
        "Spend Savings vs Uncapped",
        "Strategic Assessment",
    ]
    for col_num, h in enumerate(headers_scen, 1):
        cell = ws4.cell(row=5, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center")

    scenarios = [
        (
            "Scenario A: Full Uncapped Rollout",
            "='Inputs_Assumptions'!B14",
            "=(B6/1000)*'Inputs_Assumptions'!B7",
            "='Inputs_Assumptions'!B19",
            "=D6*'Inputs_Assumptions'!B6",
            "=E6-C6",
            "=E6/C6",
            0,
            "Standard baseline; captures full +$145.7k net profit without conversion risk",
        ),
        (
            "Scenario B1: 100-Ad Cap (100% Conversions Retained)",
            "='Inputs_Assumptions'!B29",
            "=(B7/1000)*'Inputs_Assumptions'!B7",
            "='Inputs_Assumptions'!B19",
            "=D7*'Inputs_Assumptions'!B6",
            "=E7-C7",
            "=E7/C7",
            "=C6-C7",
            "Optimistic cap scenario; saves $3,705 spend with zero conversion loss",
        ),
        (
            "Scenario B2: 100-Ad Cap (75% Conversions Retained)",
            "='Inputs_Assumptions'!B29",
            "=(B8/1000)*'Inputs_Assumptions'!B7",
            "='Inputs_Assumptions'!B19-('Inputs_Assumptions'!B30*0.25)",
            "=D8*'Inputs_Assumptions'!B6",
            "=E8-C8",
            "=E8/C8",
            "=C6-C8",
            "Conservative cap scenario; loses 290 orders ($11.6k) vs $3.7k saved",
        ),
        (
            "Scenario B3: 100-Ad Cap (50% Conversions Retained)",
            "='Inputs_Assumptions'!B29",
            "=(B9/1000)*'Inputs_Assumptions'!B7",
            "='Inputs_Assumptions'!B19-('Inputs_Assumptions'!B30*0.50)",
            "=D9*'Inputs_Assumptions'!B6",
            "=E9-C9",
            "=E9/C9",
            "=C6-C9",
            "Pessimistic cap scenario; severe conversion leakage leads to lower profit",
        ),
    ]

    for row_idx, (scen, f_imp, f_spend, f_conv, f_rev, f_prof, f_roas, f_sav, notes) in enumerate(scenarios, 6):
        ws4.cell(row=row_idx, column=1, value=scen).font = font_bold
        ws4.cell(row=row_idx, column=2, value=f_imp).number_format = "#,##0"
        ws4.cell(row=row_idx, column=3, value=f_spend).number_format = "$#,##0"
        ws4.cell(row=row_idx, column=4, value=f_conv).number_format = "#,##0"
        ws4.cell(row=row_idx, column=5, value=f_rev).number_format = "$#,##0"
        c_prof = ws4.cell(row=row_idx, column=6, value=f_prof)
        c_prof.number_format = "$#,##0"
        c_prof.font = font_bold
        c_prof.fill = fill_green
        ws4.cell(row=row_idx, column=7, value=f_roas).number_format = "0.00x"
        c_sav = ws4.cell(row=row_idx, column=8, value=f_sav)
        c_sav.number_format = "$#,##0"
        c_sav.font = font_bold
        ws4.cell(row=row_idx, column=9, value=notes).font = font_italic
        for c in range(1, 10):
            ws4.cell(row=row_idx, column=c).border = thin_border

    # -------------------------------------------------------------
    # TAB 5: Timing Hypothesis (Scenario C - Exploratory)
    # -------------------------------------------------------------
    ws5 = wb.create_sheet(title="Timing_Hypothesis")
    ws5.views.sheetView[0].showGridLines = True

    ws5["A1"] = "Scenario C: Day-of-Week Budget Shift (Exploratory Operational Hypothesis)"
    ws5["A1"].font = font_title
    ws5["A2"] = "[CAVEAT: THURSDAY AND SUNDAY WERE NOT STATISTICALLY SIGNIFICANT AFTER BONFERRONI. THIS IS A HYPOTHESIS TO TEST VIA RANDOMIZED HOLDOUT, NOT AN OPERATIONAL ROLLOUT RULE.]"
    ws5["A2"].font = font_alert

    headers_timing = [
        "Day of Week",
        "Treatment Users",
        "Observed Treatment CR",
        "Control CR",
        "Observed Lift (% pts)",
        "Bonferroni Verdict",
        "Current Media Spend (@ $2 CPM)",
        "Operational Holdout Test Plan",
    ]
    for col_num, h in enumerate(headers_timing, 1):
        cell = ws5.cell(row=5, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center")

    timing_data = [
        ("Monday", 83571, 0.033241, 0.022559, 0.010682, "Significant (p=0.0005)", "=(B6*24.8/1000)*'Inputs_Assumptions'!$B$7", "Maintain high bid priority; high-volume driver"),
        ("Tuesday", 74572, 0.030440, 0.014448, 0.015992, "Significant (p<0.0001)", "=(B7*24.8/1000)*'Inputs_Assumptions'!$B$7", "Primary candidate for budget expansion (+111% lift)"),
        ("Wednesday", 77418, 0.025356, 0.015759, 0.009597, "Significant (p=0.0004)", "=(B8*24.8/1000)*'Inputs_Assumptions'!$B$7", "Maintain steady allocation"),
        ("Thursday", 79077, 0.021637, 0.020230, 0.001407, "NOT Significant (p=0.555)", "=(B9*24.8/1000)*'Inputs_Assumptions'!$B$7", "Run randomized holdout: reduce bids 25% for 50% users"),
        ("Friday", 88805, 0.022465, 0.016303, 0.006162, "Borderline (p=0.012)", "=(B10*24.8/1000)*'Inputs_Assumptions'!$B$7", "High volume, lower lift; monitor efficiency"),
        ("Saturday", 78802, 0.021307, 0.013996, 0.007311, "Borderline (p=0.0075)", "=(B11*24.8/1000)*'Inputs_Assumptions'!$B$7", "Weekend baseline"),
        ("Sunday", 82332, 0.024620, 0.020595, 0.004025, "NOT Significant (p=0.157)", "=(B12*24.8/1000)*'Inputs_Assumptions'!$B$7", "Run randomized holdout: reduce bids 25% for 50% users"),
    ]

    for row_idx, (day, users, ad_cr, psa_cr, lift, sig, f_spend, test_plan) in enumerate(timing_data, 6):
        ws5.cell(row=row_idx, column=1, value=day).font = font_bold
        ws5.cell(row=row_idx, column=2, value=users).number_format = "#,##0"
        ws5.cell(row=row_idx, column=3, value=ad_cr).number_format = "0.00%"
        ws5.cell(row=row_idx, column=4, value=psa_cr).number_format = "0.00%"
        ws5.cell(row=row_idx, column=5, value=lift).number_format = "+0.0000%"
        c_sig = ws5.cell(row=row_idx, column=6, value=sig)
        c_sig.font = font_bold if "Significant" in sig and "NOT" not in sig else font_regular
        if "NOT" in sig:
            c_sig.fill = fill_red
        elif "Significant" in sig:
            c_sig.fill = fill_green
        ws5.cell(row=row_idx, column=7, value=f_spend).number_format = "$#,##0"
        ws5.cell(row=row_idx, column=8, value=test_plan).font = font_italic
        for c in range(1, 9):
            ws5.cell(row=row_idx, column=c).border = thin_border

    # Adjust column widths for all sheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if val_str.startswith("="):
                    max_len = max(max_len, 14)
                else:
                    max_len = max(max_len, len(val_str))
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 52)

    wb.save(output_path)
    print(f"Excel financial model saved initially to: {output_path}")

    # Use Excel COM to calculate and save formula results
    try:
        import win32com.client
        abs_output_path = os.path.abspath(output_path)
        excel_app = win32com.client.Dispatch("Excel.Application")
        excel_app.Visible = False
        excel_app.DisplayAlerts = False
        wb_com = excel_app.Workbooks.Open(abs_output_path)
        excel_app.CalculateFull()
        wb_com.Save()
        wb_com.Close()
        excel_app.Quit()
        print("Excel COM recalculation successful. All formula values are evaluated and cached in workbook.")
    except Exception as e:
        print(f"Note: Could not run Excel COM recalculation ({e}). Formulas remain fully functional on open.")


if __name__ == "__main__":
    build_excel_financial_model()
