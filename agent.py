import json
import random
from typing import Dict, Any
from pydantic import ValidationError

from llm import LLMWrapper
from prompts import SYSTEM_PROMPT, PROPOSAL_PROMPT, VENDOR_SIMULATION_PROMPT, FALLBACK_TEMPLATES
from schemas import NegotiationProposal, VendorResponse

class NegotiationAgent:
    """
    Core negotiation agent that generates proposals and simulates vendor responses
    """
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def generate_proposals(self, context: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Generate three different negotiation proposals: polite, firm, and term_swap
        
        Args:
            context: Dictionary containing vendor_message, past_price, target_price, etc.
            
        Returns:
            Dictionary with three proposal types, each containing content and reasoning
        """
        
        context_str = self._format_context(context)
        proposals = {}
        strategies = ["polite", "firm", "term_swap"]
        
        for strategy in strategies:
            proposals[strategy] = self._generate_single_proposal(
                strategy, 
                context_str, 
                context
            )
        
        return proposals
    
    def _generate_single_proposal(
        self, 
        strategy: str, 
        context_str: str, 
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a single proposal with retry logic and fallback"""
        
        prompt = PROPOSAL_PROMPT.format(
            context=context_str,
            strategy=strategy,
            past_price=context["past_price"],
            target_price=context["target_price"]
        )
        
        # First attempt
        try:
            raw = self.llm.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.65
            )
            
            proposal_data = self._parse_proposal(raw)
            return proposal_data
            
        except Exception as e:
            print(f"[PROPOSAL ERROR] {strategy} first attempt failed: {e}")
            
            # Second attempt with stricter instructions
            try:
                strict_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON with keys: proposal, reasoning, expected_outcome. No other text."
                
                raw = self.llm.generate(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=strict_prompt,
                    temperature=0.6
                )
                
                proposal_data = self._parse_proposal(raw)
                return proposal_data
                
            except Exception as e2:
                print(f"[PROPOSAL ERROR] {strategy} second attempt failed: {e2}. Using fallback.")
                return self._get_fallback_proposal(strategy, context)
    
    def _parse_proposal(self, raw: str) -> Dict[str, str]:
        """Parse and validate proposal JSON"""
        
        # Try to parse JSON
        data = json.loads(raw)
        
        # Validate with Pydantic schema
        obj = NegotiationProposal(**data)
        
        return {
            "content": obj.proposal,
            "reasoning": obj.reasoning,
            "expected_outcome": obj.expected_outcome
        }
    
    def simulate_vendor_response(
        self, 
        context: Dict[str, Any], 
        selected_proposal: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Simulate how a vendor might respond to the selected proposal
        
        Args:
            context: Original negotiation context
            selected_proposal: The proposal that was selected
            
        Returns:
            Dictionary containing vendor response and accepted price
        """
        
        prompt = VENDOR_SIMULATION_PROMPT.format(
            vendor_message=context["vendor_message"],
            proposal=selected_proposal["content"],
            original_price=context["past_price"],
            target_price=context["target_price"],
            service_type=context["service_type"],
            relationship=context["relationship"]
        )
        
        # First attempt
        try:
            raw = self.llm.generate(
                system_prompt="You are simulating a vendor's response to a negotiation. Be realistic and consider business factors.",
                user_prompt=prompt,
                temperature=0.5
            )
            
            response_data = self._parse_vendor_response(raw)
            return response_data
            
        except Exception as e:
            print(f"[VENDOR SIM ERROR] First attempt failed: {e}")
            
            # Second attempt with stricter instructions
            try:
                strict_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON with keys: response, accepted_price, reasoning, success. No other text."
                
                raw = self.llm.generate(
                    system_prompt="You are simulating a vendor's response to a negotiation. Be realistic and consider business factors.",
                    user_prompt=strict_prompt,
                    temperature=0.45
                )
                
                response_data = self._parse_vendor_response(raw)
                return response_data
                
            except Exception as e2:
                print(f"[VENDOR SIM ERROR] Second attempt failed: {e2}. Using fallback.")
                return self._get_fallback_vendor_response(context)
    
    def _parse_vendor_response(self, raw: str) -> Dict[str, Any]:
        """Parse and validate vendor response JSON"""
        
        # Try to parse JSON
        data = json.loads(raw)
        
        # Validate with Pydantic schema
        obj = VendorResponse(**data)
        
        return {
            "content": obj.response,
            "accepted_price": obj.accepted_price,
            "reasoning": obj.reasoning,
            "success": obj.success
        }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the LLM"""
        return f"""
<vendor_message>{context['vendor_message']}</vendor_message>
<current_price>${context['past_price']}/month</current_price>
<target_price>${context['target_price']}/month</target_price>
<service_type>{context['service_type']}</service_type>
<relationship_length>{context['relationship']}</relationship_length>
"""
    
    def _get_fallback_proposal(self, strategy: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate dynamic fallback proposals when LLM fails"""
        
        target_price = context.get('target_price', 'a more competitive rate')
        
        templates = FALLBACK_TEMPLATES.get(strategy, FALLBACK_TEMPLATES['polite'])
        
        content = (
            f"{templates['opening']}. {templates['transition']}, "
            f"{templates['ask']} around ${target_price}/month. {templates['closing']}."
        )
        
        return {
            "content": content,
            "reasoning": f"Using {strategy} approach with fallback template due to LLM error.",
            "expected_outcome": "Vendor is likely to be receptive to a discussion."
        }
    
    def _get_fallback_vendor_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a dynamic fallback vendor response when simulation fails"""
        
        original_price = context.get("past_price", 1000)
        target_price = context.get("target_price", 800)
        
        # Simulate a realistic concession (25-75% of requested discount)
        requested_discount = original_price - target_price
        actual_discount = requested_discount * random.uniform(0.25, 0.75)
        accepted_price = round(original_price - actual_discount, 2)
        
        response_text = (
            f"Thank you for your proposal. After reviewing our options, "
            f"we can offer a revised rate of ${accepted_price}/month. "
            f"This reflects our commitment to our partnership while maintaining "
            f"our service quality standards."
        )
        
        return {
            "content": response_text,
            "accepted_price": accepted_price,
            "reasoning": "Fallback simulation: partial concession based on typical vendor behavior.",
            "success": accepted_price < original_price
        }
    
    def get_engine_info(self) -> Dict[str, str]:
        """Get information about the current LLM engine"""
        return self.llm.get_engine_info()


class DebateOrchestrator:
    """
    Orchestrates debates between different negotiation strategies (STRETCH GOAL)
    """
    
    def __init__(self):
        self.llm = LLMWrapper()
    
    def conduct_debate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Have polite and firm agents debate, then pick the best strategy
        
        Args:
            context: Negotiation context
            
        Returns:
            Best strategy recommendation with reasoning
        """
        
        debate_prompt = f"""
You are orchestrating a debate between two negotiation experts:

POLITE AGENT POSITION:
- Relationship-building leads to long-term success
- Collaborative language builds trust and goodwill
- Win-win solutions create lasting partnerships
- Aggressive tactics can backfire and damage relationships

FIRM AGENT POSITION:
- Clear boundaries establish respect and credibility
- Market leverage should be used when available
- Direct communication saves time and shows confidence
- Vendors respect customers who know their value

CONTEXT:
{self._format_debate_context(context)}

Have each agent make their case, then recommend the optimal strategy for this situation.

Return JSON format:
{{
    "polite_argument": "Key points for collaborative approach",
    "firm_argument": "Key points for direct approach",
    "recommendation": "polite|firm|hybrid",
    "reasoning": "Why this approach is best for this situation"
}}
"""
        
        try:
            response = self.llm.generate(
                system_prompt="You are a negotiation strategy orchestrator conducting an expert debate.",
                user_prompt=debate_prompt,
                temperature=0.7
            )
            
            data = json.loads(response)
            return data
            
        except Exception as e:
            print(f"[DEBATE ERROR] {e}. Using fallback recommendation.")
            # Fallback recommendation
            return {
                "polite_argument": "Building relationships leads to long-term success and repeat business.",
                "firm_argument": "Clear boundaries establish respect and better outcomes in negotiations.",
                "recommendation": "polite",
                "reasoning": "Default to collaborative approach for relationship preservation when debate fails."
            }
    
    def _format_debate_context(self, context: Dict[str, Any]) -> str:
        """Format context for debate prompt"""
        return f"""
- Service: {context.get('service_type', 'Unknown')}
- Current Price: ${context.get('past_price', 0)}/month
- Target Price: ${context.get('target_price', 0)}/month
- Relationship: {context.get('relationship', 'Unknown')}
- Vendor Message: {context.get('vendor_message', 'N/A')[:200]}...
"""


# Utility function for testing
def test_agent():
    """Test the agent with a sample negotiation"""
    
    agent = NegotiationAgent()
    
    test_context = {
        "vendor_message": "Your renewal is coming up at $1000/month for the Pro plan.",
        "past_price": 500,
        "target_price": 400,
        "service_type": "SaaS Subscription",
        "relationship": "1-3 Years"
    }
    
    print("=" * 60)
    print("TESTING NEGOTIATION AGENT")
    print("=" * 60)
    
    # Test proposal generation
    print("\n1. Generating proposals...")
    try:
        proposals = agent.generate_proposals(test_context)
        print("Proposals generated successfully!")
        
        for strategy, proposal in proposals.items():
            print(f"\n{strategy.upper()}:")
            print(f"  Content: {proposal['content'][:100]}...")
            print(f"  Reasoning: {proposal['reasoning'][:100]}...")
    except Exception as e:
        print(f"Proposal generation failed: {e}")
        return False
    
    # Test vendor simulation
    print("\n2. Simulating vendor response...")
    try:
        selected = proposals['polite']
        response = agent.simulate_vendor_response(test_context, selected)
        print("Vendor response simulated successfully!")
        print(f"  Accepted Price: ${response['accepted_price']}/month")
        print(f"  Success: {response['success']}")
    except Exception as e:
        print(f"Vendor simulation failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_agent()
