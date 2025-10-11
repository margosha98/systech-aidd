"""LLM клиент для работы с Openrouter API."""
import logging
from openai import AsyncOpenAI

from src.config import Config
from src.storage.models import Message

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для работы с LLM через Openrouter."""
    
    def __init__(self, config: Config):
        """Инициализация LLM клиента.
        
        Args:
            config: Объект конфигурации
        """
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key,
            timeout=config.llm_timeout
        )
        self.model = config.openrouter_model
        self.temperature = config.llm_temperature
        self.max_tokens = config.llm_max_tokens
        
        logger.info(f"LLMClient initialized with model: {self.model}")
    
    async def get_response(self, messages: list[Message], system_prompt: str) -> str:
        """Получает ответ от LLM с учетом истории.
        
        Args:
            messages: История сообщений
            system_prompt: Системный промпт
            
        Returns:
            Ответ от LLM
            
        Raises:
            Exception: При ошибке API
        """
        logger.info(f"Sending request to LLM: history_length={len(messages)}")
        logger.debug(f"Messages: {[{'role': m.role, 'content': m.content[:50]} for m in messages]}")
        
        try:
            # Формируем список сообщений для API
            api_messages = [{"role": "system", "content": system_prompt}]
            
            # Добавляем историю диалога
            for msg in messages:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Received response from LLM: length={len(answer)}")
            logger.debug(f"LLM response: {answer}")
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise



