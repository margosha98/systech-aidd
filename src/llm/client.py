"""LLM клиент для работы с Openrouter API."""
import logging
from openai import AsyncOpenAI

from src.config import Config

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
    
    async def get_response(self, user_message: str, system_prompt: str) -> str:
        """Получает ответ от LLM.
        
        Args:
            user_message: Сообщение пользователя
            system_prompt: Системный промпт
            
        Returns:
            Ответ от LLM
            
        Raises:
            Exception: При ошибке API
        """
        logger.info(f"Sending request to LLM: message_length={len(user_message)}")
        logger.debug(f"User message: {user_message}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
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



