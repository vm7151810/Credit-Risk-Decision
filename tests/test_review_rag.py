from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_rag import ReviewRAGService


class ReviewRAGPromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ReviewRAGService(Path("knowledge_base"), Path(tempfile.gettempdir()))
        self.applicant = {
            "credit_amount": 7882,
            "duration_in_month": 42,
            "credit_history": "A32",
        }
        self.prediction = {
            "decision": "Review",
            "pd": 0.2832,
            "decision_reason": (
                "guarantor support decreases risk; longer loan duration increases risk"
            ),
        }

    def test_prompt_preserves_human_decision_boundary(self) -> None:
        prompt = self.service._build_prompt(
            self.applicant,
            self.prediction,
            "[Source 1: Guidelines on loan origination and monitoring, page 36]",
        )

        self.assertIn("Do not make, recommend, or imply a final approve/reject decision", prompt)
        self.assertIn("mitigating context, not a concern", prompt)
        self.assertIn("checks and actions directly related to risk-increasing factors", prompt)
        self.assertNotIn("'credit_history': 'A32'", prompt)
        self.assertNotIn("'credit_amount': 7882", prompt)

    def test_non_review_case_is_rejected_before_retrieval(self) -> None:
        with self.assertRaises(ValueError):
            self.service.summarize_review_case(
                self.applicant,
                {**self.prediction, "decision": "Approve"},
            )

    def test_generated_text_is_ascii_normalized_for_audit_output(self) -> None:
        text = self.service._normalize_generated_text(
            "\u201cReview\u201d \u2013 analyst\u2019s evidence"
        )

        self.assertEqual(text, '"Review" - analyst\'s evidence')

    def test_retrieval_query_excludes_mitigating_factors(self) -> None:
        query = self.service._build_query(self.applicant, self.prediction)

        self.assertIn("longer loan duration increases risk", query)
        self.assertNotIn("guarantor support decreases risk", query)

    def test_review_note_guard_blocks_consumer_irrelevant_actions(self) -> None:
        violations = self.service._note_violations(
            "2. Evidence to verify\nAssess refinancing in capital markets [Source 1].",
            self.prediction,
        )

        self.assertTrue(any("refinanc" in item for item in violations))
        self.assertTrue(any("capital market" in item for item in violations))

    def test_official_pdf_sources_are_loaded_as_the_knowledge_base(self) -> None:
        files = self.service._get_knowledge_files()

        self.assertTrue(files)
        self.assertTrue(all(path.suffix == ".pdf" for path in files))
        self.assertTrue(
            any("EBA_GL_2020_06" in path.name for path in files),
        )


class GeminiCascadeLLMTests(unittest.TestCase):
    def test_cascade_falls_back_when_primary_model_fails(self) -> None:
        from unittest.mock import MagicMock
        from review_rag import GeminiCascadeLLM

        llm = GeminiCascadeLLM(
            models=["gemini-3.8-flash", "gemini-3.5-flash-lite"],
            api_key="test-api-key",
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "1. Why this case needs review\nRisk factors.\n2. Evidence to verify\n[Source 1]\n3. Suggested analyst action\nReview [Source 1]."

        # First model fails, second model succeeds
        def fake_generate(model: str, contents: str) -> Any:
            if model == "gemini-3.8-flash":
                raise RuntimeError("Rate limit / Model unavailable")
            return mock_response

        mock_client.models.generate_content.side_effect = fake_generate
        llm._client = mock_client

        output = llm.invoke("Test prompt")
        self.assertIn("Why this case needs review", output)
        self.assertEqual(llm.model_name, "gemini-3.5-flash-lite")

    def test_cascade_raises_runtime_error_when_all_fail(self) -> None:
        from unittest.mock import MagicMock
        from review_rag import GeminiCascadeLLM

        llm = GeminiCascadeLLM(
            models=["gemini-3.8-flash", "gemini-3.5-flash-lite"],
            api_key="test-api-key",
        )

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("Service Unavailable")
        llm._client = mock_client

        with self.assertRaises(RuntimeError) as ctx:
            llm.invoke("Test prompt")
        self.assertIn("All Gemini models in fallback cascade failed", str(ctx.exception))

    def test_missing_api_key_raises_runtime_error(self) -> None:
        import os
        from review_rag import GeminiCascadeLLM

        original_key = os.environ.get("GEMINI_API_KEY")
        try:
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            llm = GeminiCascadeLLM(api_key="")
            with self.assertRaises(RuntimeError) as ctx:
                llm.invoke("Test prompt")
            self.assertIn("GEMINI_API_KEY is not set", str(ctx.exception))
        finally:
            if original_key is not None:
                os.environ["GEMINI_API_KEY"] = original_key


if __name__ == "__main__":
    unittest.main()

