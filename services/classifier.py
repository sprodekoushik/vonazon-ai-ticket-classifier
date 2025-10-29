# services/classifier.py
from typing import List, Dict, Any
import os, json, re
from core.schemas import ClassificationRequest, ClassificationResult
from services.deepseek_client import chat_completion, DEEPSEEK_API_KEY
from services import deepseek_client

print("DEEPSEEK_API_KEY loaded:", bool(DEEPSEEK_API_KEY))

SYSTEM_PROMPT = (
    "You are a precise ticket classifier.\n"
    "Given a ticket and a fixed list of categories, respond ONLY as JSON with keys: "
    "{category, confidence, explanation}.\n"
    "Rules:\n"
    "- Use one of the provided categories only.\n"
    "- confidence is a float 0..1.\n"
    "- Keep explanation brief.\n"
)

def _fallback_rule_based(text: str, categories: List[str]) -> Dict[str, Any]:
    t = text.lower()

    def pick(name: str, default: str = None) -> str:
        if name in categories:
            return name
        return default or (categories[-1] if categories else "Other")

    if any(k in t for k in ["invoice", "charge", "billing", "payment", "paid"]):
        cat = pick("Billing")
    elif any(k in t for k in ["login", "password", "bug", "error", "crash", "cant log", "cannot log"]):
        cat = pick("Technical Issue")
    elif any(k in t for k in ["plan", "pricing", "buy", "purchase", "quote", "subscription"]):
        cat = pick("Sales Inquiry")
    elif any(k in t for k in ["refund", "refunded", "money back"]):
        cat = pick("Refunds")
    else:
        cat = pick("Other")

    return {"category": cat, "confidence": 0.55, "explanation": "Rule-based fallback"}

def _safe_json_extract(content: str) -> Dict[str, Any]:
    # strip code fences if present
    m = re.search(r"```(?:json)?\n(.*?)\n```", content, re.DOTALL)
    json_text = m.group(1) if m else content
    try:
        return json.loads(json_text)
    except Exception:
        # try to carve first JSON object
        m2 = re.search(r"\{.*\}", content, re.DOTALL)
        if m2:
            try:
                return json.loads(m2.group(0))
            except Exception:
                pass
    return {"category": "Other", "confidence": 0.3, "explanation": "Parse error; defaulted"}

def classify(req: ClassificationRequest) -> List[ClassificationResult]:
    # --- Force reload environment each run (Streamlit safe) ---
    from dotenv import load_dotenv
    load_dotenv(override=True)
    import os
    from services import deepseek_client
    deepseek_client.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    print("🔑 DeepSeek key loaded in classify:", bool(deepseek_client.DEEPSEEK_API_KEY))
    # ----------------------------------------------------------

    results: List[ClassificationResult] = []
    categories = req.categories or ["Other"]


    for t in req.tickets:
        use_fallback = not bool(DEEPSEEK_API_KEY)
        pred: Dict[str, Any]
        print("Using fallback? ->", not bool(DEEPSEEK_API_KEY))

        if not use_fallback:
            try:
                user_prompt = (
                    f"Categories: {categories}\n"
                    f"Ticket: {t.text}\n"
                    "Return ONLY JSON like "
                    '{"category":"...","confidence":0.0,"explanation":"..."}'
                )
                response = chat_completion(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=req.model,
                    temperature=req.temperature,
                )
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                pred = _safe_json_extract(content)
                pred["raw"] = response
            except Exception:
                # network/auth/HTTP/parsing errors -> fallback
                pred = _fallback_rule_based(t.text, categories)
        else:
            pred = _fallback_rule_based(t.text, categories)

        results.append(ClassificationResult(
            ticket_id=t.id,
            ticket_text=t.text,
            category=pred.get("category", "Other"),
            confidence=float(pred.get("confidence", 0.5)),
            explanation=pred.get("explanation"),
            raw=pred.get("raw") if "raw" in pred else None,
        ))
    return results
