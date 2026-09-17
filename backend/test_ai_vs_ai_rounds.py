import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from negotiation_runner import run_negotiation
from agents.orchestrator_agent import OrchestratorAgent
from agents.reasoning_engine import ReasoningEngine
from agents.counteroffer_evaluator import CounterofferEvaluator
from agents.practice_store import practice_store


from agents.practice_agent import extract_offer_from_text


class TestAiVsAiRounds(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # NATURAL LANGUAGE OFFER EXTRACTION TESTS
    # --------------------------------------------------------------------------
    def test_natural_language_buyer_offer_extractions(self):
        cases = [
            ("I will offer 1 crore for this property.", 10000000.0),
            ("I can offer 1.2 crore.", 12000000.0),
            ("I will give 50 lakhs.", 5000000.0),
            ("I can do 65L", 6500000.0),
            ("My offer is 2500000", 2500000.0),
            ("I can pay ₹1.5 Cr", 15000000.0),
            ("I will offer 1.10 crore for this property.", 11000000.0),
            ("I can offer ₹1.49 Cr.", 14900000.0),
            ("I will give 1 crore", 10000000.0),
            ("I can offer 1 crore", 10000000.0),
            ("I will give 1 crore for this property.", 10000000.0),
        ]
        for text, expected in cases:
            extracted = extract_offer_from_text(text)
            self.assertEqual(
                extracted,
                expected,
                f"Failed for text '{text}': expected {expected}, got {extracted}"
            )

    # --------------------------------------------------------------------------
    # TEST: Verify AI-vs-AI history stores BOTH natural message and numeric offer
    # --------------------------------------------------------------------------
    def test_ai_vs_ai_history_stores_message_and_extracted_offer(self):
        orchestrator = OrchestratorAgent(["Buyer Agent", "Seller Agent"])
        buyer_reasoning = ReasoningEngine(
            role="Buyer Agent",
            persona="collaborative",
            goals="buy property",
            target_price=10000000.0,
            minimum_price=8000000.0,
            maximum_price=12000000.0
        )
        seller_reasoning = ReasoningEngine(
            role="Seller Agent",
            persona="collaborative",
            goals="sell property",
            target_price=14000000.0,
            minimum_price=11000000.0,
            maximum_price=15000000.0
        )
        buyer_eval = CounterofferEvaluator(
            role="buyer",
            target_price=10000000.0,
            minimum_price=8000000.0,
            maximum_price=12000000.0
        )
        seller_eval = CounterofferEvaluator(
            role="seller",
            target_price=14000000.0,
            minimum_price=11000000.0,
            maximum_price=15000000.0
        )

        result = run_negotiation(
            orchestrator=orchestrator,
            buyer_reasoning=buyer_reasoning,
            seller_reasoning=seller_reasoning,
            buyer_evaluator=buyer_eval,
            seller_evaluator=seller_eval,
            property_data={"Property Title": "Emerald Heights Villa"},
            reference_price=15000000.0,
            max_rounds=3
        )

        history = result["negotiation_history"]
        self.assertGreater(len(history), 0)

        # Buyer entry in round 1
        buyer_entry = history[0]
        self.assertEqual(buyer_entry["agent"], "Buyer Agent")
        self.assertEqual(buyer_entry["sender"], "ai_buyer")
        self.assertIsInstance(buyer_entry["message"], str)
        self.assertIn("offer", buyer_entry["message"].lower())
        self.assertIsNotNone(buyer_entry.get("offer"))
        self.assertIsInstance(buyer_entry["offer"], float)

        # Seller entry in round 1
        seller_entry = history[1]
        self.assertEqual(seller_entry["agent"], "Seller Agent")
        self.assertEqual(seller_entry["sender"], "ai_seller")
        self.assertIsInstance(seller_entry["message"], str)
        self.assertIsNotNone(seller_entry.get("offer"))
        self.assertIsNotNone(seller_entry.get("decision"))
        self.assertIsNotNone(seller_entry.get("reason"))
        self.assertIn("concession step", seller_entry["reason"])

    # --------------------------------------------------------------------------
    # TEST: Agreement at round 3 with Seller as final speaker
    # --------------------------------------------------------------------------
    def test_00_agreement_at_round_3_seller_final_speaker(self):
        orchestrator = OrchestratorAgent(["Buyer Agent", "Seller Agent"])
        buyer_eval = MagicMock()
        seller_eval = MagicMock()
        buyer_reasoning = MagicMock()
        seller_reasoning = MagicMock()

        def buyer_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 3:
                return {"decision": "COUNTER", "counter_price": 10000000 + r * 100000}
            else:
                return {"decision": "COUNTER", "counter_price": 11000000.0}

        def seller_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 3:
                return {"decision": "COUNTER", "counter_price": 13000000 - r * 100000}
            else:
                return {"decision": "ACCEPT", "accepted_price": 11000000.0}

        buyer_eval.evaluate.side_effect = buyer_eval_side_effect
        seller_eval.evaluate.side_effect = seller_eval_side_effect
        buyer_reasoning.generate_response.return_value = "I can offer ₹1.10 Cr for this property."
        seller_reasoning.generate_response.return_value = "I accept your offer of ₹1.10 Cr."

        result = run_negotiation(
            orchestrator=orchestrator,
            buyer_reasoning=buyer_reasoning,
            seller_reasoning=seller_reasoning,
            buyer_evaluator=buyer_eval,
            seller_evaluator=seller_eval,
            property_data={"title": "Test Villa"},
            reference_price=13000000.0,
            max_rounds=10
        )

        self.assertIn(result["status"], ["ACCEPTED", "AGREEMENT_REACHED"])
        self.assertEqual(result["agreed_price"], 11000000.0)
        self.assertEqual(result["round"], 3)
        self.assertEqual(result["completed_rounds"], 3)
        self.assertEqual(result["max_rounds"], 10)
        self.assertEqual(orchestrator.round_count, 3)

        history = result["negotiation_history"]
        self.assertEqual(len(history), 6) # 3 buyer + 3 seller
        final_message = history[-1]
        self.assertEqual(final_message["agent"], "Seller Agent")
        self.assertEqual(final_message["sender"], "ai_seller")
        self.assertEqual(final_message.get("decision"), "AGREE")
        self.assertIn("DECISION: AGREE", final_message["message"])
        self.assertIn("We agreed with your price.", final_message["message"])
        self.assertEqual(final_message["round"], 3)

        # Confirm there is no Round 4 or extra buyer message
        rounds = [item["round"] for item in history]
        self.assertEqual(rounds, [1, 1, 2, 2, 3, 3])
        self.assertNotIn(4, rounds)

    # --------------------------------------------------------------------------
    # TEST 1 & TEST 4 & TEST 5: Agreement at round 7 with max_rounds = 10
    # --------------------------------------------------------------------------
    def test_01_agreement_at_round_7(self):
        orchestrator = OrchestratorAgent(["Buyer Agent", "Seller Agent"])
        buyer_eval = MagicMock()
        seller_eval = MagicMock()
        buyer_reasoning = MagicMock()
        seller_reasoning = MagicMock()

        # Let rounds 1-6 be counters, round 7 be agreement
        def buyer_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 7:
                return {"decision": "COUNTER", "counter_price": 10000000 + r * 100000}
            else:
                return {"decision": "COUNTER", "counter_price": 12500000.0}

        def seller_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 7:
                return {"decision": "COUNTER", "counter_price": 15000000 - r * 100000}
            else:
                return {"decision": "ACCEPT", "accepted_price": 12500000.0}

        buyer_eval.evaluate.side_effect = buyer_eval_side_effect
        seller_eval.evaluate.side_effect = seller_eval_side_effect
        buyer_reasoning.generate_response.return_value = "I can offer ₹1.25 Cr for this property."
        seller_reasoning.generate_response.return_value = "I accept your offer of ₹1.25 Cr."

        result = run_negotiation(
            orchestrator=orchestrator,
            buyer_reasoning=buyer_reasoning,
            seller_reasoning=seller_reasoning,
            buyer_evaluator=buyer_eval,
            seller_evaluator=seller_eval,
            property_data={"title": "Test Property"},
            reference_price=15000000.0,
            max_rounds=10
        )

        # Status and price
        self.assertIn(result["status"], ["ACCEPTED", "AGREEMENT_REACHED"])
        self.assertEqual(result["agreed_price"], 12500000.0)

        # Completed rounds must be 7, max_rounds must be 10
        self.assertEqual(result["round"], 7)
        self.assertEqual(result["completed_rounds"], 7)
        self.assertEqual(result["max_rounds"], 10)
        self.assertEqual(orchestrator.round_count, 7)

        # Final seller message must be AGREE
        history = result["negotiation_history"]
        final_message = history[-1]
        self.assertEqual(final_message["agent"], "Seller Agent")
        self.assertEqual(final_message.get("decision"), "AGREE")
        self.assertIn("DECISION: AGREE", final_message["message"])
        self.assertIn("We agreed with your price.", final_message["message"])
        self.assertNotIn("DECISION: COUNTER", final_message["message"])
        self.assertNotIn("COUNTEROFFER", final_message["message"])

        # TEST 4: No rounds 8, 9, 10 generated
        rounds_in_history = set(item["round"] for item in history)
        self.assertEqual(rounds_in_history, {1, 2, 3, 4, 5, 6, 7})
        self.assertNotIn(8, rounds_in_history)
        self.assertNotIn(9, rounds_in_history)
        self.assertNotIn(10, rounds_in_history)

        # TEST 5: History contains only rounds 1-7
        self.assertTrue(all(1 <= item["round"] <= 7 for item in history))

    # --------------------------------------------------------------------------
    # TEST 2: Agreement at round 4 with max_rounds = 10
    # --------------------------------------------------------------------------
    def test_02_agreement_at_round_4(self):
        orchestrator = OrchestratorAgent(["Buyer Agent", "Seller Agent"])
        buyer_eval = MagicMock()
        seller_eval = MagicMock()
        buyer_reasoning = MagicMock()
        seller_reasoning = MagicMock()

        def buyer_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 4:
                return {"decision": "COUNTER", "counter_price": 5000000 + r * 100000}
            else:
                return {"decision": "COUNTER", "counter_price": 6000000.0}

        def seller_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            if r < 4:
                return {"decision": "COUNTER", "counter_price": 7000000 - r * 100000}
            else:
                return {"decision": "ACCEPT", "accepted_price": 6000000.0}

        buyer_eval.evaluate.side_effect = buyer_eval_side_effect
        seller_eval.evaluate.side_effect = seller_eval_side_effect
        buyer_reasoning.generate_response.return_value = "I will offer ₹60.00 Lakhs for this property."
        seller_reasoning.generate_response.return_value = "Seller accepts"

        result = run_negotiation(
            orchestrator=orchestrator,
            buyer_reasoning=buyer_reasoning,
            seller_reasoning=seller_reasoning,
            buyer_evaluator=buyer_eval,
            seller_evaluator=seller_eval,
            property_data={"title": "Test Property"},
            reference_price=7000000.0,
            max_rounds=10
        )

        self.assertIn(result["status"], ["ACCEPTED", "AGREEMENT_REACHED"])
        self.assertEqual(result["agreed_price"], 6000000.0)
        self.assertEqual(result["round"], 4)
        self.assertEqual(result["completed_rounds"], 4)
        self.assertEqual(result["max_rounds"], 10)
        self.assertEqual(orchestrator.round_count, 4)

        history = result["negotiation_history"]
        final_message = history[-1]
        self.assertEqual(final_message["agent"], "Seller Agent")
        self.assertEqual(final_message.get("decision"), "AGREE")
        self.assertIn("DECISION: AGREE", final_message["message"])
        self.assertIn("We agreed with your price.", final_message["message"])

        rounds_in_history = set(item["round"] for item in history)
        self.assertEqual(rounds_in_history, {1, 2, 3, 4})
        self.assertNotIn(5, rounds_in_history)

    # --------------------------------------------------------------------------
    # TEST 3: No agreement with max_rounds = 10 (reaches max rounds without agreement)
    # --------------------------------------------------------------------------
    def test_03_no_agreement_max_rounds(self):
        orchestrator = OrchestratorAgent(["Buyer Agent", "Seller Agent"])
        buyer_eval = MagicMock()
        seller_eval = MagicMock()
        buyer_reasoning = MagicMock()
        seller_reasoning = MagicMock()

        # Buyer moves from 50L up by 10k each round, Seller moves from 100L down by 10k
        def buyer_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            return {"decision": "COUNTER", "counter_price": 5000000.0 + r * 10000.0}

        def seller_eval_side_effect(incoming_offer, previous_offer, reference_price):
            r = orchestrator.round_count
            return {"decision": "COUNTER", "counter_price": 10000000.0 - r * 10000.0}

        buyer_eval.evaluate.side_effect = buyer_eval_side_effect
        seller_eval.evaluate.side_effect = seller_eval_side_effect
        buyer_reasoning.generate_response.return_value = "I can offer ₹50.10 Lakhs."
        seller_reasoning.generate_response.return_value = "Thank you for your offer. I can counter at ₹99.90 Lakhs."

        result = run_negotiation(
            orchestrator=orchestrator,
            buyer_reasoning=buyer_reasoning,
            seller_reasoning=seller_reasoning,
            buyer_evaluator=buyer_eval,
            seller_evaluator=seller_eval,
            property_data={"title": "Test Property"},
            reference_price=10000000.0,
            max_rounds=10
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertIsNone(result["agreed_price"])
        self.assertEqual(result["round"], 10)
        self.assertEqual(result["completed_rounds"], 10)
        self.assertEqual(result["max_rounds"], 10)
        self.assertEqual(orchestrator.round_count, 10)

    # --------------------------------------------------------------------------
    # TEST 6: Human vs AI Practice Mode remains unaffected and fully functional
    # --------------------------------------------------------------------------
    def test_06_human_vs_ai_unaffected(self):
        start_payload = {
            "scenario": 2,
            "property_index": 0,
            "human_role": "buyer",
            "ai_personality": "collaborative",
            "max_rounds": 10
        }
        resp = self.client.post("/negotiations/practice", json=start_payload)
        self.assertEqual(resp.status_code, 200)
        neg_id = resp.json()["negotiation_id"]

        # Check initial state
        state_resp = self.client.get(f"/negotiations/{neg_id}")
        self.assertEqual(state_resp.status_code, 200)
        state = state_resp.json()
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["round"], 1)
        self.assertEqual(state["max_rounds"], 10)

        # Send human natural offer
        msg_resp = self.client.post(
            f"/negotiations/{neg_id}/message",
            json={"message": "I will give 1 crore"}
        )
        self.assertEqual(msg_resp.status_code, 200)
        data = msg_resp.json()
        self.assertEqual(data["human_offer"], 10000000.0)
        self.assertIn("ai_response", data)
        self.assertEqual(data["round"], 1)

    # --------------------------------------------------------------------------
    # TEST 7: AI vs AI API endpoint returns synchronized rounds and downloads work
    # --------------------------------------------------------------------------
    def test_07_ai_vs_ai_endpoint_and_reports(self):
        ai_payload = {
            "scenario": 2,
            "buyer_personality": 2,
            "seller_personality": 2,
            "max_rounds": 8
        }
        resp = self.client.post("/negotiations", json=ai_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        neg_id = data.get("negotiation_id")
        self.assertIsNotNone(neg_id)
        self.assertIn("round", data)
        self.assertIn("completed_rounds", data)
        self.assertIn("max_rounds", data)
        self.assertEqual(data["max_rounds"], 8)
        self.assertGreaterEqual(data["completed_rounds"], 1)
        self.assertLessEqual(data["completed_rounds"], 8)

        # Test state endpoint
        state_resp = self.client.get(f"/negotiations/{neg_id}")
        self.assertEqual(state_resp.status_code, 200)
        state_data = state_resp.json()
        self.assertEqual(state_data["round"], data["completed_rounds"])
        self.assertEqual(state_data["max_rounds"], 8)

        # Test transcript download contains natural language buyer message
        t_resp = self.client.get(f"/negotiations/{neg_id}/transcript?format=txt")
        self.assertEqual(t_resp.status_code, 200)
        self.assertIn("NEGOTIATION TRANSCRIPT", t_resp.text)
        self.assertIn("BUYER", t_resp.text)
        self.assertIn("offer", t_resp.text.lower())

        # Test summary report download
        s_resp = self.client.get(f"/negotiations/{neg_id}/summary?format=json")
        self.assertEqual(s_resp.status_code, 200)
        s_data = s_resp.json()
        self.assertEqual(s_data["executive_summary"]["total_rounds"], data["completed_rounds"])


if __name__ == "__main__":
    unittest.main()
