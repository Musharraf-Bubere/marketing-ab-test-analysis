# Phase 6: Business Impact & Commercial Decision Analysis Report

> [!IMPORTANT] Disclaimer on Financial Assumptions
> All financial figures (Gross Margin per Conversion, CPM, Total Spend, Net Profit) in this report are **HYPOTHETICAL PLANNING ASSUMPTIONS** designed to demonstrate commercial viability and sensitivity boundaries. The conversion lift (+0.7692% pts) and sample counts (564,577 users, 14,014,692 impressions) are empirical figures from executed data.

---

## 1. Executive Summary of Financial Findings

Under our base-case assumptions (**$40 gross margin per conversion** and **$2.00 CPM**):
* **Base Case Net Profit**: The campaign generates **$173,720 in incremental gross profit** against **$28,029 in media spend**, yielding **+$145,691 in net incremental profit** with a **6.20× margin-based return on ad spend (ROAS)** and a Customer Acquisition Cost (**CAC**) of **$6.45 per incremental conversion**.
* **Downside Protection (95% CI Lower Bound)**: In the conservative statistical scenario (3,360 incremental orders), net profit remains strongly positive at **+$106,371** with a **4.79× margin-based return** and **$8.34 CAC**.
* **Substantial Safety Cushion**: The campaign breaks even at a **CPM of $12.40** (base) and **$9.59** (conservative). At current market display rates of $2.00 CPM, the business has a **nearly 5× margin of safety**.
* **The Frequency Cap Tradeoff**: Capping exposure at 100 ads saves **$3,705 in ad spend**. However, because display ads are inexpensive ($0.002/impression) while orders carry substantial margin ($40), losing more than **93 incremental orders (about 8% of the tier's lift)** negates the entire cost savings. Crucially, the 100+ tier is still profitable on its own (generating ~$11.42 in gross profit per $2.00 of media cost). Therefore, a frequency cap should be evaluated as a holdout experiment rather than rolled out immediately.

---

## 2. Financial Performance Across Statistical Bounds

| Performance Metric | Conservative (95% CI Low) | Base Case (Point Estimate) | Optimistic (95% CI High) | Formula / Derivation |
| :--- | :--- | :--- | :--- | :--- |
| **Incremental Conversions** | **3,360** | **4,343** | **5,326** | Derived from 95% CI bounds: $[+0.595\%\text{ pts}, +0.943\%\text{ pts}]$ |
| **Gross Margin / Conversion** | **$40.00** | **$40.00** | **$40.00** | Hypothetical baseline assumption |
| **Incremental Gross Profit** | **$134,400** | **$173,720** | **$213,040** | $\text{Incremental Conversions} \times \text{Gross Margin}$ |
| **Total Ad Impressions Served** | 14,014,692 | 14,014,692 | 14,014,692 | Empirical total from treatment cohort |
| **Cost per 1,000 Impressions (CPM)**| **$2.00** | **$2.00** | **$2.00** | Hypothetical market display baseline |
| **Total Campaign Media Spend** | **$28,029** | **$28,029** | **$28,029** | $(\text{Total Impressions} / 1,000) \times \text{CPM}$ |
| **Net Incremental Profit** | **+$106,371** | **+$145,691** | **+$185,011** | $\text{Incremental Gross Profit} - \text{Media Spend}$ |
| **Margin-based ROAS** | **4.79×** (479%) | **6.20×** (620%) | **7.60×** (760%) | $\text{Incremental Gross Profit} / \text{Media Spend}$ |
| **Cost / Incremental Order (CAC)** | **$8.34** | **$6.45** | **$5.26** | $\text{Media Spend} / \text{Incremental Conversions}$ |

---

## 3. Explicit Break-Even Analysis

To give leadership definitive decision thresholds, we computed the exact mathematical break-even points:

### 1. Break-Even CPM (Maximum Viable Ad Cost at $40 Margin)
$$\text{Break-Even CPM} = \frac{\text{Incremental Conversions} \times \text{Gross Margin}}{\text{Total Impressions} / 1,000}$$
* **Base Case**: $\mathbf{\$12.40\text{ CPM}}$
* **Conservative (95% CI Low)**: $\mathbf{\$9.59\text{ CPM}}$
* **Optimistic (95% CI High)**: $\mathbf{\$15.20\text{ CPM}}$
* *Leadership Takeaway*: The media buying team can pay up to **$9.59 CPM** under the conservative statistical scenario before the campaign turns unprofitable. At $2.00 CPM, profitability is highly insulated against media inflation.

### 2. Break-Even Gross Margin per Conversion (Minimum Margin at $2.00 CPM)
$$\text{Break-Even Margin} = \frac{\text{Media Spend}}{\text{Incremental Conversions}} = \text{CAC}$$
* **Base Case**: $\mathbf{\$6.45\text{ per order}}$
* **Conservative (95% CI Low)**: $\mathbf{\$8.34\text{ per order}}$
* **Optimistic (95% CI High)**: $\mathbf{\$5.26\text{ per order}}$
* *Leadership Takeaway*: Even if order margins compress from $40 down to **$8.34**, the campaign still covers its ad costs.

---

## 4. 2D Sensitivity Matrix: Net Incremental Profit ($)

Evaluating net profit across a grid of **CPM ($1 to $10)** and **Gross Margin ($5 to $100)** under base incremental conversions (4,343):

| CPM \ Margin | $5 | $10 | $20 | $30 | $40 (Base) | $50 | $60 | $75 | $100 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$1.00** | +$7,700 | +$29,415 | +$72,845 | +$116,275 | **+$159,705** | +$203,135 | +$246,565 | +$311,710 | +$420,285 |
| **$2.00 (Base)**| -$6,315 | +$15,401 | +$58,831 | +$102,261 | **+$145,691** | +$189,121 | +$232,551 | +$297,696 | +$406,271 |
| **$3.00** | -$20,329 | +$1,386 | +$44,816 | +$88,246 | **+$131,676** | +$175,106 | +$218,536 | +$283,681 | +$392,256 |
| **$4.00** | -$34,344 | -$12,628 | +$30,802 | +$74,232 | **+$117,662** | +$161,092 | +$204,522 | +$269,667 | +$378,242 |
| **$5.00** | -$48,359 | -$26,643 | +$16,787 | +$60,217 | **+$103,647** | +$147,077 | +$190,507 | +$255,652 | +$364,227 |
| **$6.00** | -$62,374 | -$40,658 | +$2,773 | +$46,203 | **+$89,633** | +$133,063 | +$176,493 | +$241,638 | +$350,213 |
| **$8.00** | -$90,403 | -$68,687 | -$25,257 | +$18,173 | **+$61,603** | +$105,033 | +$148,463 | +$213,608 | +$322,183 |
| **$10.00** | -$118,432 | -$96,717 | -$53,286 | -$9,856 | **+$33,574** | +$77,004 | +$120,434 | +$185,579 | +$294,154 |

*Key Sensitivity Takeaways*:
* **Loss-making conditions**:
  - At very low margins ($5), the campaign is unprofitable at any CPM of $2.00 or higher (e.g., -$6.3k at $2 CPM).
  - At $10 margin, losses begin once CPM reaches $4.00.
  - At moderate margins ($20), losses emerge when CPM reaches $8.00+.
  - At $30 margin, losses occur at $10.00 CPM.
* **Profit-making stability**: At our baseline ($40 margin) and above, the campaign remains profitable across every tested CPM from $1.00 to $10.00.

---

## 5. Strategic Comparison: Uncapped vs. Frequency Capped

In the 100+ exposure tier, 22,054 users consumed 4,058,074 impressions and generated 1,159 incremental conversions. Capping this tier at 100 impressions removes only impressions **after the 100th**, saving **1,852,674 impressions** ($3,705 in media spend) while ensuring every user still receives up to 100 impressions.

Because users still receive 100 impressions, assuming 25% or 50% conversion loss in that tier represents conservative planning scenarios. We evaluate Scenario B across three explicit retention levels:

| Strategy Scenario | Total Impressions | Media Spend (@ $2 CPM) | Spend Saved vs Uncapped | Incremental Orders | Incremental Gross Profit (@ $40 Margin) | Net Incremental Profit | Margin-based ROAS | Strategic Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario A: Full Uncapped Rollout** | 14,014,692 | $28,029 | Baseline ($0) | **4,343** | $173,720 | **+$145,691** | **6.20×** | Standard baseline; high profit, zero conversion risk |
| **Scenario B1: 100-Ad Cap (100% Retention)** | 12,162,018 | $24,324 | +$3,705 | **4,343** | $173,720 | **+$149,396** | **7.14×** | Best-case cap; saves $3.7k with zero order loss (+2.5% profit gain) |
| **Scenario B2: 100-Ad Cap (75% Retention)** | 12,162,018 | $24,324 | +$3,705 | **4,053** (-290 orders) | $162,120 (-$11.6k) | **+$137,796** | **6.67×** | **Net profit decreases by $7,895** because lost margin ($11.6k) > spend saved ($3.7k) |
| **Scenario B3: 100-Ad Cap (50% Retention)** | 12,162,018 | $24,324 | +$3,705 | **3,763** (-580 orders) | $150,520 (-$23.2k) | **+$126,196** | **6.19×** | **Net profit decreases by $19,495** due to severe conversion leakage |

> [!WARNING] The Frequency Capping Asymmetry & Productivity Insight
> It is vital to recognize that the 100+ tier is **not loss-making**:
> * That tier generates **0.286 incremental orders per 1,000 impressions**, translating to **$11.42 in gross profit per 1,000 impressions** ($0.286 \times \$40$). Against a $2.00 CPM, this tier still yields a **5.7× return**.
> * However, its efficiency is lower than the 51–100 tier (which generates $33.76 in gross profit per 1k impressions, or 16.9× return).
> * The breakeven retention threshold is **92.0%**:
>   $$\text{Breakeven Order Loss Threshold} = \frac{\$3,705\text{ spend saved}}{\$40\text{ margin}} = 92.6\text{ orders}$$
> If capping exposure causes the company to lose more than **93 orders out of the 1,159 generated in that tier** (an 8% loss), the cap results in lower net profit. Because the dollar savings ($3.7k) is small relative to potential lost margin, testing the cap on an isolated holdout group is the only responsible approach.

---

## 6. Scenario C: Timing Reallocation (Exploratory Hypothesis)

* **The Observation**: Monday ($p = 0.0005$) and Tuesday ($p < 0.0001$) show statistically validated lifts of +47% and +111% relative. Thursday ($p = 0.555$) and Sunday ($p = 0.157$) show no significant lift after Bonferroni correction.
* **The Caveat**: *Absence of evidence is not evidence of absence*. Daily control sample sizes (~3k users) are small and low-powered.
* **The Operational Recommendation**: Do not immediately shut off Thursday or Sunday spend. Instead, **run a randomized holdout test** reducing bids by 25% for a random half of users on those days over several weeks, setting sample sizes and MDE in advance, and evaluating success on net incremental profit.

---

## 7. Executive Decision Framework: The Rollout Recommendation

### Primary Recommendation: **Launch the Campaign (Uncapped), and Treat the 100-Ad Cap as a Holdout Test**

| Decision Path | Conditions & Criteria | Expected Commercial Outcome |
| :--- | :--- | :--- |
| **1. Launch Fully (Uncapped) [PRIMARY]** | • Margin $\ge \$40$, CPM $\le \$3.00$.<br>• Holdout testing for frequency cap is set up as Phase 2. | **Immediate deployment**: Captures full +$145.7k net incremental profit (6.20× margin-based return) with zero risk of conversion leakage. |
| **2. Test 100-Ad Cap via Holdout Group** | • Ad platform supports randomized holdout groups.<br>• Measure whether incremental orders in 100+ tier remain above 92%. | Isolates potential +$3.7k media savings while safeguarding customer orders. |
| **3. Do Not Launch** | • CPM exceeds **$9.59** (conservative break-even).<br>• Gross margin per conversion falls below **$8.34**.<br>• Production holdout test reveals lift disappears at scale. | Halt campaign rollout; ad delivery costs exceed customer lifetime value. |
