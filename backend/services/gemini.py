from dotenv import load_dotenv

load_dotenv()

import json
import logging
import os
from threading import Lock

from google import genai
from google.genai import errors
from google.genai import types

logger = logging.getLogger("heatlens.gemini")

SYSTEM_INSTRUCTION = """
You are the HeatLens Intelligence Interpreter & Analyst.
Your role is exclusively to explain and contextualize VERIFIED statistical outputs provided to you in JSON.

CRITICAL GUARDRAILS:
1. NEVER invent, modify, or estimate numerical values.
2. ALL temperature, correlation, score, and anomaly metrics MUST originate from the supplied context.
3. NEVER claim correlation implies causation. State statistical relationships using clear terms (e.g., "showed a strong positive linear relationship").
4. If a user asks for unavailable data, explicitly state that it is missing or outside FortyGuard coverage.
5. Keep explanations clear, grounded, and professional.
"""

# Dedicated instruction for Q&A mode, separate from the summary-generation instruction above.
# Summaries (interpret_results) and direct-answer Q&A (query_analyst) need different behavior —
# sharing one instruction was pulling query answers toward generic "describe everything" summaries
# instead of focused, relevant answers to the actual question asked.
ANALYST_QUERY_INSTRUCTION = SYSTEM_INSTRUCTION + """

ADDITIONAL RULES FOR THIS Q&A MODE:
6. Answer ONLY the specific question asked. Do not summarize the entire dataset.
7. Use only the JSON fields that are actually relevant to the question. Ignore unrelated fields in the context even if present.
8. If the exact field/metric needed to answer is not present in the supplied context, say plainly what is missing — do not substitute a related-but-different field and present it as the answer.
9. If the question is unrelated to heat exposure, climate, or the supplied data (e.g. small talk, general knowledge, coding help), politely state that you can only answer questions about this HeatLens analysis, and do not attempt to answer it anyway.
10. Keep the answer to 2-4 sentences unless the question explicitly asks for more detail or a breakdown.
"""


class GeminiService:
    def __init__(self):
        # Clear any conflicting Google Cloud environment variables
        # that might interfere with the Developer API Key authentication
        os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
        os.environ.pop('GOOGLE_AUTH_URI', None)
        os.environ.pop('GOOGLE_TOKEN_URI', None)

        configured_keys = os.getenv("GEMINI_API_KEYS", "")
        legacy_key = os.getenv("GEMINI_API_KEY", "")
        api_keys = [key.strip() for key in configured_keys.split(",") if key.strip()]
        if legacy_key.strip() and legacy_key.strip() not in api_keys:
            api_keys.append(legacy_key.strip())

        self._clients = []
        self._active_client_index = 0
        self._client_lock = Lock()

        for api_key in api_keys:
            if api_key.startswith("AIzaSyxxxx"):
                continue
            try:
                # Force Developer API Key auth (bypasses Google Cloud OAuth / ADC)
                self._clients.append(genai.Client(api_key=api_key))
            except Exception as e:
                logger.error("Failed to initialize a Gemini client: %s", e)

        # Keep the public attribute for compatibility with existing integrations.
        self.client = self._clients[0] if self._clients else None
        if self._clients:
            logger.info("Initialized %d Gemini API client(s)", len(self._clients))
        else:
            logger.warning("Gemini service running in unauthenticated fallback mode.")

    @staticmethod
    def _is_rate_limit_error(error: Exception) -> bool:
        return getattr(error, "code", None) == 429 or getattr(error, "status_code", None) == 429

    def _generate_content(self, *, prompt: str, config: types.GenerateContentConfig):
        """Generate content, moving to the next key when a client is rate limited."""
        if not self._clients:
            raise RuntimeError("No Gemini clients are configured")

        with self._client_lock:
            start_index = self._active_client_index
            clients = [
                self._clients[(start_index + offset) % len(self._clients)]
                for offset in range(len(self._clients))
            ]

        last_rate_limit_error = None
        for offset, client in enumerate(clients):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config,
                )
                if offset:
                    with self._client_lock:
                        self._active_client_index = (start_index + offset) % len(self._clients)
                        self.client = self._clients[self._active_client_index]
                    logger.info("Gemini request succeeded after rotating API key")
                return response
            except Exception as error:
                if not self._is_rate_limit_error(error):
                    raise
                last_rate_limit_error = error
                logger.warning(
                    "Gemini API key %d is rate limited; trying the next configured key",
                    (start_index + offset) % len(self._clients) + 1,
                )

        raise last_rate_limit_error or RuntimeError("All Gemini clients are rate limited")

    def interpret_results(self, structured_analysis: dict) -> str:
        if not self.client:
            score = structured_analysis.get('heat_exposure_score', {})
            stats = structured_analysis.get('descriptive_statistics', {}).get('temperature', {})
            persistence = structured_analysis.get('persistence', {})
            intensity = score.get('classification', 'UNKNOWN EXPOSURE')
            return (
                f"The area '{structured_analysis.get('location_name')}' is experiencing {intensity} conditions "
                f"(Score: {score.get('overall_score', 'N/A')}/100). Peak temperature has reached {stats.get('max', 'N/A')}°C, "
                f"with continuous hot conditions persisting for approximately {persistence.get('longest_continuous_hot_spell_hours', 'N/A')} hours. "
                f"This suggests significant thermal stress on urban environments and vulnerable populations."
            )

        prompt = f"""
Analyze and interpret these computed heat statistics for human understanding:
```json
{json.dumps(structured_analysis, indent=2)}
```
Write a concise 3-sentence executive summary of what this data actually means for safety and urban heat impact."""
        try:
            response = self._generate_content(
                prompt=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                ),
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini interpretation error: {e}")
            # Provide clean fallback without exposing error details
            score = structured_analysis.get('heat_exposure_score', {})
            stats = structured_analysis.get('descriptive_statistics', {}).get('temperature', {})
            persistence = structured_analysis.get('persistence', {})
            intensity = score.get('classification', 'UNKNOWN EXPOSURE')
            return (
                f"The area '{structured_analysis.get('location_name')}' is experiencing {intensity} conditions "
                f"(Score: {score.get('overall_score', 'N/A')}/100). Peak temperature has reached {stats.get('max', 'N/A')}°C, "
                f"with continuous hot conditions persisting for approximately {persistence.get('longest_continuous_hot_spell_hours', 'N/A')} hours. "
                f"This suggests significant thermal stress on urban environments and vulnerable populations."
            )

    def query_analyst(self, user_query: str, context: dict | None) -> str:
        user_query = user_query.strip()
        context = context or {}
        if not self.client:
            return self._analyst_fallback(user_query, context)

        prompt = f"""
Current Backend Calculated Context:
```json
{json.dumps(context or {}, indent=2)}
```

User Question: "{user_query}"

Instructions:
- Identify which specific field(s) in the context above are needed to answer this exact question.
- Answer using only those fields. Do not describe unrelated parts of the context.
- If the needed field is missing from the context, say so explicitly instead of guessing or generalizing.
- If the question is outside the scope of this heat exposure data, say so instead of answering generically.
- Be direct and specific — reference the actual figures involved.
"""
        try:
            response = self._generate_content(
                prompt=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=ANALYST_QUERY_INSTRUCTION,
                    temperature=0.2,
                ),
            )
            answer = (response.text or '').strip()
            return answer or self._analyst_fallback(user_query, context)
        except errors.ClientError as e:
            if getattr(e, "code", None) in (401, 403):
                logger.warning("Gemini authentication failed; using analytical fallback")
            else:
                logger.error(f"Gemini AI Analyst client error: {e}")
            return self._analyst_fallback(user_query, context)
        except errors.APIError as e:
            logger.error(f"Gemini AI Analyst API error: {e}")
            return self._analyst_fallback(user_query, context)
        except Exception as e:
            logger.error(f"Gemini AI Analyst query error: {e}")
            return self._analyst_fallback(user_query, context)

    @staticmethod
    def _analyst_fallback(user_query: str, context: dict | None) -> str:
        context = context or {}
        score = context.get("heat_exposure_score", {})
        breakdown = score.get("breakdown", {})
        persistence = context.get("persistence", {})
        statistics = context.get("descriptive_statistics", {}).get("temperature", {})

        overall_score = score.get("overall_score", "N/A")
        classification = score.get("classification", "the recorded exposure")
        intensity = breakdown.get("intensity_component", "N/A")
        persistence_component = breakdown.get("persistence_component", "N/A")
        anomaly = breakdown.get("anomaly_component", "N/A")
        environmental = breakdown.get("environmental_component", "N/A")
        hot_spell = persistence.get("longest_continuous_hot_spell_hours", "N/A")
        peak = statistics.get("max", "N/A")

        query = user_query.lower()
        if "correl" in query or "humidity" in query:
            correlations = context.get("correlations", [])
            humidity_pairs = [
                pair for pair in correlations
                if "humidity" in str(pair.get("variable_x", "")).lower()
                or "humidity" in str(pair.get("variable_y", "")).lower()
            ]
            if humidity_pairs:
                pair = humidity_pairs[0]
                other_variable = pair.get("variable_y", pair.get("variable_x", "temperature"))
                return (
                    f"Humidity and {other_variable} showed a {pair.get('strength', 'measured')} "
                    f"{pair.get('direction', '')} relationship (correlation {pair.get('coefficient', 'N/A')}) "
                    f"across {pair.get('sample_size', 'N/A')} observations. "
                    "This describes a statistical relationship, not causation."
                )
            return "No humidity correlation was included in the calculated analysis context."

        if "why" in query or "high" in query or "score" in query:
            return (
                f"The exposure score is {overall_score}/100 ({classification}). "
                f"Its calculated components are intensity ({intensity}), persistence ({persistence_component}), "
                f"anomalies ({anomaly}), and environmental conditions ({environmental}). "
                "These components explain the score mathematically and do not establish causation."
            )

        return (
            f"The calculated exposure score is {overall_score}/100, classified as {classification}. "
            f"It reflects the combined contribution of intensity ({intensity}), persistence "
            f"({persistence_component}), anomalies ({anomaly}), and environmental conditions "
            f"({environmental}); these calculated factors explain how the score was derived rather "
            f"than indicating causation. The recorded peak temperature was {peak}°C, with the longest "
            f"continuous hot spell lasting {hot_spell} hours."
        )


gemini_service = GeminiService()