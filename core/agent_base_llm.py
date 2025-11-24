# core/agent_base_llm.py

from core.llm_client import GeminiClient

class LLMAgent:
    def __init__(self, role_name, system_instruction, toolset=None, model="gemini-pro"):
        """
        role_name: 'Coordinator', 'DataLoader', 'Analyzer', 'Recommender', 'Critic'
        system_instruction: System prompt describing the agent's role and objectives
        toolset: List of Python tools for function calling (ADK/wrappers)
        """
        self.role_name = role_name
        self.system_instruction = system_instruction
        self.tools = toolset or []
        self.llm = GeminiClient(model=model)

    async def act(self, user_input, context=None):
        """
        Execute the agent's role via LLM with optional function calling.
        user_input: the main task or query for the agent
        context: extended context (dict)
        """
        prompt = self.build_prompt(user_input, context)
        result = await self.llm.call(
            prompt=prompt,
            tools=self.tools,
            system_instruction=self.system_instruction
        )
        return result

    def build_prompt(self, user_input, context=None):
        """
        Compose the agent's prompt, including user input, context, and instructions.
        """
        context_block = f"\n[Context]\n{context}" if context else ""
        prompt = (
            f"You are {self.role_name}. {self.system_instruction}\n"
            f"{context_block}\n"
            f"[Task]\n{user_input}"
        )
        return prompt

    def register_tools(self, tools):
        """Dynamically attach Python tools for function calling (ADK style)."""
        self.tools = tools
