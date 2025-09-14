import torch
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from threading import Lock
import logging

class LocalLLMModel:
    def __init__(self, model_name="meta-llama/Llama-3.2-1B", device=None):
        """
        Initialize the local LLM model
        Args:
            model_name: HuggingFace model name (default: DialoGPT for conversation)
            device: Device to run model on (auto-detects if None)
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.model_lock = Lock()  # Ensure thread-safe model access

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Load model and tokenizer asynchronously"""
        self.logger.info(f"Loading model {self.model_name} on {self.device}")

        # Load model and tokenizer in executor to prevent blocking
        loop = asyncio.get_event_loop()

        def load_model():
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
            model.to(self.device)

            # Set proper pad token for Llama - use a different token than EOS
            if tokenizer.pad_token is None:
                # Try to use a proper pad token, fallback to EOS if needed
                if hasattr(tokenizer, 'unk_token') and tokenizer.unk_token:
                    tokenizer.pad_token = tokenizer.unk_token
                else:
                    tokenizer.pad_token = tokenizer.eos_token

            return tokenizer, model

        self.tokenizer, self.model = await loop.run_in_executor(None, load_model)
        self.logger.info("Model loaded successfully!")

    async def generate_response(self, system_message: str, messages: list, max_tokens: int = 256) -> str:
        """
        Generate response from conversation history
        Args:
            system_message: System prompt
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
        Returns:
            Generated response string
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        # Format conversation for model input
        conversation_text = self._format_conversation(system_message, messages)

        # Run generation in executor to prevent blocking
        loop = asyncio.get_event_loop()

        def generate():
            with self.model_lock:  # Ensure thread-safe access
                # Tokenize input with attention mask
                tokenized = self.tokenizer(
                    conversation_text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=2048
                )
                input_ids = tokenized['input_ids'].to(self.device)
                attention_mask = tokenized['attention_mask'].to(self.device)

                # Generate response with anti-repetition parameters
                with torch.no_grad():
                    outputs = self.model.generate(
                        input_ids,
                        attention_mask=attention_mask,
                        max_new_tokens=max_tokens,
                        # min_new_tokens=10,
                        # num_return_sequences=1,
                        temperature=0.3,
                        do_sample=True,
                        top_p=0.95,
                        top_k=50,
                        # repetition_penalty=1.3,  # Higher penalty to reduce repetition
                        # no_repeat_ngram_size=3,  # Prevent 3-gram repetition
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )

                # Decode only the new tokens (response)
                response_tokens = outputs[0][input_ids.shape[1]:]
                response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)

                return response.strip()

        return await loop.run_in_executor(None, generate)

    def _format_conversation(self, system_message: str, messages: list) -> str:
        """Format conversation for model input"""
        # Start with system message
        formatted = f"System: {system_message}\n\n"

        # Add conversation history
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted += f"{role}: {content}\n"

        # Add Assistant prompt to encourage response
        formatted += "Assistant:"

        return formatted

class LlamaLocalLLM(LocalLLMModel):
    def __init__(self, device=None):
        super().__init__("meta-llama/Llama-3.2-1B", device)

    def _format_conversation(self, system_message: str, messages: list) -> str:
        """Simple conversation format that works better with Llama 3.2"""
        # Start with system instruction
        formatted = f"System: {system_message}\n\n"

        # Add recent conversation history (only last 3 messages to avoid confusion)
        recent_messages = messages[-3:] if len(messages) > 3 else messages

        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            formatted += f"{role}: {content}\n\n"

        # Add prompt for assistant response
        formatted += "Assistant:"

        return formatted