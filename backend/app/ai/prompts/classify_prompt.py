"""
Classification prompt — instructs the LLM to assign category and risk level.
Full prompt implemented in Phase 3.
"""

CLASSIFY_SYSTEM_PROMPT = """\
You are a pharmaceutical quality risk assessor.
Based on the complaint below, assign:

1. category: one of [Product Quality Defect, Packaging Defect, Labeling Error,
   Delivery Damage, Adverse Event, Foreign Material, Documentation Error, Other]

2. risk_level: one of [High, Medium, Low] using these criteria:
   - High:   patient safety impact or likely regulatory reportability
   - Medium: product quality concern with limited patient exposure
   - Low:    cosmetic, packaging, or documentation issue with no safety implication

Return ONLY a valid JSON object:
{
  "category":   "<category>",
  "risk_level": "<High|Medium|Low>"
}
"""

CLASSIFY_USER_TEMPLATE = (
    "Product: {product_name}\n"
    "Summary: {complaint_summary}\n\n"
    "Full text:\n{cleaned_text}"
)
