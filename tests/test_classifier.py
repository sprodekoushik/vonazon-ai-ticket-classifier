# tests/test_classifier.py
from core.schemas import Ticket, ClassificationRequest, ClassificationResult
from services import classifier

def test_rule_based_fallback_basic():
    req = ClassificationRequest(
        tickets=[
            Ticket(id="1", text="My invoice has extra charges."),
            Ticket(id="2", text="I can't login, password invalid."),
            Ticket(id="3", text="Tell me about your pricing plan."),
            Ticket(id="4", text="When will my refund arrive?"),
            Ticket(id="5", text="Something unrelated."),
        ],
        categories=["Billing", "Technical Issue", "Sales Inquiry", "Refunds", "Other"],
        model="deepseek-chat",
        temperature=0.0,
    )
    out = classifier.classify(req)
    cats = [r.category for r in out]
    assert cats[:4] == ["Billing", "Technical Issue", "Sales Inquiry", "Refunds"]
    assert cats[4] in {"Other", "Billing", "Technical Issue", "Sales Inquiry", "Refunds"}  # graceful catch-all
    for r in out:
        assert isinstance(r, ClassificationResult)

def test_deepseek_path_with_mock(monkeypatch):
    """
    Force the DeepSeek branch by setting a fake key and monkeypatching the API call.
    """
    # 1) pretend key is present
    import os
    os.environ["DEEPSEEK_API_KEY"] = "sk-test"

    # 2) patch the API function to return a fake JSON-like completion
    from services import deepseek_client

    def fake_chat_completion(messages, model=None, temperature=0.0):
        # The classifier expects choices[0].message.content to be JSON or contain JSON
        return {
            "choices": [{
                "message": {
                    "content": '{"category":"Billing","confidence":0.91,"explanation":"Invoice-related"}'
                }
            }]
        }

    monkeypatch.setattr(deepseek_client, "chat_completion", fake_chat_completion)

    req = ClassificationRequest(
        tickets=[Ticket(id="T1", text="Please help, invoice is wrong.")],
        categories=["Billing", "Technical Issue", "Sales Inquiry", "Refunds", "Other"],
        model="deepseek-chat",
        temperature=0.0,
    )
    out = classifier.classify(req)
    assert len(out) == 1
    assert out[0].category == "Billing"
    assert 0.0 <= out[0].confidence <= 1.0
