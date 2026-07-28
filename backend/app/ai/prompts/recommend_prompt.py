"""
Recommendation prompt — instructs the LLM to generate root cause and CAPA.
Full prompt implemented in Phase 3.
"""

RECOMMEND_SYSTEM_PROMPT = """\
You are a pharmaceutical GMP expert and CAPA specialist.
Based on the complaint details below, provide:

1. root_cause_recommendation: a concise hypothesis of the likely root cause (2-4 sentences).
2. capa_recommendation: specific, actionable corrective and preventive actions appropriate
   for a pharmaceutical manufacturing environment (3-5 bullet points as a single string).

Return ONLY a valid JSON object:
{
  "root_cause_recommendation": "<root cause hypothesis>",
  "capa_recommendation":       "<CAPA actions>"
}
"""

RECOMMEND_USER_TEMPLATE = (
    "Product: {product_name}\n"
    "Batch: {batch_number}\n"
    "Category: {category}\n"
    "Risk Level: {risk_level}\n"
    "Summary: {complaint_summary}"
)
