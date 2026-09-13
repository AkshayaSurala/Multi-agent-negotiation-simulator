import os
import re

from dotenv import load_dotenv
from google import genai
from agents.practice_agent import format_inr


class ReasoningEngine:
    """
    LLM reasoning engine for the real-estate negotiation simulator.

    IMPORTANT:

    The CounterofferEvaluator controls the actual negotiation
    decision and price.

    Gemini is responsible only for generating the natural-language
    negotiation message.

    If Gemini is unavailable, a deterministic fallback response
    is returned.
    """

    def __init__(
        self,
        role,
        persona,
        goals,
        target_price,
        minimum_price,
        maximum_price
    ):

        load_dotenv()

        self.role = role
        self.persona = persona
        self.goals = goals

        self.target_price = float(target_price)
        self.minimum_price = float(minimum_price)
        self.maximum_price = float(maximum_price)

        # =====================================================
        # GEMINI CONFIGURATION
        # =====================================================

        self.client = None

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        # Gemini is optional.
        # The negotiation must still work without it.
        if api_key:

            try:

                self.client = genai.Client(
                    api_key=api_key
                )

            except Exception as error:

                print(
                    "\nGemini client could not be initialized."
                )

                print(
                    f"Reason: {error}"
                )

                self.client = None

        else:

            print(
                "\nGEMINI_API_KEY is not set."
            )

            print(
                "Using deterministic negotiation responses."
            )

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash"
        )

    # =========================================================
    # GENERATE RESPONSE
    # =========================================================

    def generate_response(
        self,
        negotiation_history,
        evaluation
    ):
        """
        Generate the agent's response.

        Interface:

            generate_response(history, evaluation)

        The evaluator controls:

            ACCEPT
            COUNTER

        and the actual price.
        """

        if evaluation is None:
            evaluation = {}

        decision = str(
            evaluation.get(
                "decision",
                "COUNTER"
            )
        ).upper()

        incoming_offer = evaluation.get(
            "incoming_offer"
        )

        counter_price = evaluation.get(
            "counter_price"
        )

        accepted_price = evaluation.get(
            "accepted_price"
        )

        previous_offer = evaluation.get(
            "previous_offer"
        )

        prompt = self._build_prompt(
            negotiation_history=negotiation_history,
            decision=decision,
            incoming_offer=incoming_offer,
            counter_price=counter_price,
            accepted_price=accepted_price,
            previous_offer=previous_offer
        )

        response = self._generate_with_gemini(
            prompt
        )

        if response:

            return self._clean_response(
                response
            )

        return self._fallback_response(
            decision=decision,
            incoming_offer=incoming_offer,
            counter_price=counter_price,
            accepted_price=accepted_price
        )

    # =========================================================
    # GEMINI REQUEST
    # =========================================================

    def _generate_with_gemini(
        self,
        prompt
    ):
        """
        Send request to Gemini.

        Returns None if Gemini is unavailable.
        """

        if self.client is None:
            return None

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
            )

            if response is None:
                return None

            text = getattr(
                response,
                "text",
                None
            )

            if not text:
                return None

            return text.strip()

        except Exception as error:

            print(
                "\nGemini temporarily unavailable."
            )

            print(
                f"Reason: {error}"
            )

            print(
                "Using deterministic negotiation response."
            )

            return None

    # =========================================================
    # BUILD PROMPT
    # =========================================================

    def _build_prompt(
        self,
        negotiation_history,
        decision,
        incoming_offer,
        counter_price,
        accepted_price,
        previous_offer
    ):

        history_text = self._format_history(
            negotiation_history
        )

        incoming_text = self._format_price(
            incoming_offer
        )

        previous_text = self._format_price(
            previous_offer
        )

        counter_text = self._format_price(
            counter_price
        )

        accepted_text = self._format_price(
            accepted_price
        )

        is_buyer = "buyer" in str(self.role).lower()

        if is_buyer:
            if decision in ["ACCEPT", "AGREE"]:
                role_instructions = f"""You are accepting the seller's offer. Output exactly:
DECISION: AGREE

We agreed with your price.

Agreed Price: {accepted_text}"""
            else:
                role_instructions = f"""You are the buyer making a price offer of {counter_text}.
Generate a concise, natural-language negotiation sentence stating your offer clearly (for example: "I will offer {counter_text} for this property." or "I can offer {counter_text}.").
Do NOT output code blocks, JSON, or markdown headers. Return only your natural spoken sentence containing your offer."""
        else:
            if decision in ["ACCEPT", "AGREE"]:
                role_instructions = f"""You are the seller accepting the buyer's offer. Output exactly:
DECISION: AGREE

We agreed with your price.

Agreed Price: {accepted_text}"""
            else:
                role_instructions = f"""You are the seller countering with {counter_text} in response to the buyer's offer of {incoming_text}.
Generate a polite, professional natural-language counteroffer sentence (for example: "Thank you for your offer of {incoming_text}. I can come down to {counter_text} to help us reach a deal." or "I appreciate your proposal. Let's move closer to an agreement at {counter_text}.").
Do NOT output code blocks, JSON, or markdown headers. Return only your natural spoken sentence containing your counteroffer."""

        return f"""
You are the {self.role} in an AI-vs-AI real-estate negotiation.

ROLE:
{self.role}

PERSONALITY:
{self.persona}

GOALS:
{self.goals}

YOUR TARGET PRICE:
{self._format_price(self.target_price)}

YOUR MINIMUM PRICE:
{self._format_price(self.minimum_price)}

YOUR MAXIMUM PRICE:
{self._format_price(self.maximum_price)}

PREVIOUS OFFER FROM YOU:
{previous_text}

LATEST OFFER FROM OTHER AGENT:
{incoming_text}

EVALUATOR DECISION:
{decision}

EVALUATOR COUNTEROFFER:
{counter_text}

ACCEPTED PRICE:
{accepted_text}

NEGOTIATION HISTORY:
{history_text}

INSTRUCTIONS:
{role_instructions}
"""

    # =========================================================
    # FORMAT HISTORY
    # =========================================================

    def _format_history(
        self,
        history
    ):

        if not history:
            return "No previous negotiation messages."

        lines = []

        for entry in history:

            round_number = entry.get(
                "round",
                "?"
            )

            agent = entry.get(
                "agent",
                "Unknown Agent"
            )

            message = entry.get(
                "message",
                ""
            )

            lines.append(
                f"Round {round_number} | "
                f"{agent}:\n{message}"
            )

        return "\n\n".join(
            lines
        )

    # =========================================================
    # FALLBACK RESPONSE
    # =========================================================

    def _fallback_response(
        self,
        decision,
        incoming_offer,
        counter_price,
        accepted_price
    ):

        if decision in ["ACCEPT", "AGREE"]:

            price = accepted_price

            if price is None:
                price = incoming_offer

            return (
                "DECISION: AGREE\n\n"
                "We agreed with your price.\n\n"
                f"Agreed Price: "
                f"{self._format_price(price)}"
            )

        is_buyer = "buyer" in str(self.role).lower()

        if is_buyer:
            price = counter_price if counter_price is not None else incoming_offer
            return self._generate_buyer_fallback(price, incoming_offer)

        price = counter_price if counter_price is not None else incoming_offer
        return self._generate_seller_fallback(price, incoming_offer)

    def _generate_buyer_fallback(
        self,
        offer_price,
        incoming_offer=None
    ):
        if offer_price is None:
            offer_price = self.target_price

        formatted = self._format_price(offer_price)
        persona_str = str(self.persona).lower()

        if "aggressive" in persona_str:
            if incoming_offer:
                return f"I can offer {formatted}."
            return f"I will offer {formatted} for this property."
        elif "risk" in persona_str:
            if incoming_offer:
                return f"I can offer {formatted}."
            return f"I can offer {formatted}."
        else:
            if incoming_offer:
                return f"I can offer {formatted}."
            return f"I will offer {formatted} for this property."

    def _generate_seller_fallback(
        self,
        counter_price,
        incoming_offer=None
    ):
        if counter_price is None:
            counter_price = self.target_price

        counter_str = self._format_price(counter_price)
        incoming_str = (
            self._format_price(incoming_offer)
            if incoming_offer is not None
            else "your initial offer"
        )
        persona_str = str(self.persona).lower()

        if "aggressive" in persona_str:
            return f"Your offer of {incoming_str} is too low. My revised price is {counter_str}."
        elif "risk" in persona_str:
            return f"Thank you for {incoming_str}. Based on the property valuation, I can counter at {counter_str}."
        else:
            if incoming_offer:
                return f"Thank you for your offer of {incoming_str}. I can come down to {counter_str} to help us reach a deal."
            return f"I appreciate your proposal. Let's move closer to an agreement at {counter_str}."

    # =========================================================
    # CLEAN RESPONSE
    # =========================================================

    def _clean_response(
        self,
        response
    ):

        text = response.strip()

        if text.startswith("```"):

            text = re.sub(
                r"```[a-zA-Z]*",
                "",
                text
            )

            text = text.replace(
                "```",
                ""
            )

        return text.strip()

    # =========================================================
    # FORMAT PRICE
    # =========================================================

    def _format_price(
        self,
        price
    ):

        if price is None:
            return "N/A"

        return format_inr(price)