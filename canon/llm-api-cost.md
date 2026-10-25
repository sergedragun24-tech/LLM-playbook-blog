# Канон: стоимость LLM API — проверенные цифры и механика тарификации

Собрано 11.08.2026 при проверке статьи по теме. Все цифры сняты с первичных источников (документация вендоров, пресс-релизы Gartner, официальные тарифные приложения).

## Соотношение input / output

Выходные токены дороже входных в 5–6 раз — на всех проверенных прайсах. Это не «почти всегда дороже», а стабильный множитель, его можно называть цифрой.

| Модель | Input / 1M | Output / 1M | Множитель |
|---|---|---|---|
| Claude Opus 5 | $5 | $25 | 5× |
| Claude Sonnet 5 | $2 | $10 | 5× |
| Claude Haiku 4.5 | $1 | $5 | 5× |
| gpt-5.6-sol | $2,50 | $15 | 6× |
| gpt-5.6-luna | $0,10 | $0,60 | 6× |

Источники: https://platform.claude.com/docs/en/about-claude/pricing · https://developers.openai.com/api/docs/pricing
Примечание: цена Claude Sonnet 5 $2/$10 — вводная до 31.08.2026, с 01.09.2026 становится $3/$15. Цифру в статьях без даты не публиковать.

## Разрыв между флагманом и облегчённой моделью

- gpt-5.6-sol против gpt-5.6-luna: **25× по входным токенам** ($2,50 против $0,10) и **25× по выходным** ($15 против $0,60).
- Claude Opus 5 против Haiku 4.5: **5×** ($5/$25 против $1/$5).

То есть «разница может быть кратной» — недооценка. Внутри одного вендора разрыв доходит до 25 раз.

## Prompt caching (кеширование промптов)

Ключевое: кеширование **не бесплатно**, и в статьях его нельзя подавать как безусловную экономию.

**Anthropic** (https://platform.claude.com/docs/en/build-with-claude/prompt-caching):
- cache read = **0,1× цены input** (то есть на 90% дешевле);
- cache write = **1,25×** базовой цены input для 5-минутного кеша и **2×** для часового;
- TTL по умолчанию **5 минут**, час — за доп. плату; кеш обновляется бесплатно при каждом обращении;
- минимальная длина кешируемого префикса зависит от модели: 512 токенов (Opus 5), 1024 (Sonnet 5, Opus 4.8), 2048, 4096 (Haiku 4.5, Opus 4.5/4.6). Дословно: «Shorter prompts cannot be cached, even if marked with cache_control».

**OpenAI** (https://developers.openai.com/api/docs/guides/prompt-caching):
- кешированный input дешевле в 10 раз ($2,50 → $0,25 для gpt-5.6-sol);
- cache write = 1,25× для GPT-5.6 и новее;
- минимум 1024 токена (для GPT-5.5 и ранее — 1024–2048);
- «A cached prefix remains eligible for reuse for at least 30 minutes».

**Вывод для статей:** при редких обращениях кеширование увеличивает счёт (заплатил 1,25× за запись, кеш истёк через 5 минут неиспользованным). Экономия появляется только при плотном потоке однотипных запросов с общим префиксом длиннее минимального порога.

## Длинного контекста как отдельной надбавки у Anthropic НЕТ

Дословно: «Claude 4.6 and later models and Claude Mythos Preview include the full 1M token context window at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.)»

**Следствие:** писать «за длинный контекст берут надбавку» — фактическая ошибка. Корректная формулировка: платишь линейно за каждый переданный токен, а в диалоге переданный объём накапливается от хода к ходу — отсюда нелинейный рост стоимости диалога, а не нелинейный тариф.

## Reasoning-токены тарифицируются как выходные и не видны через API

Дословно из документации OpenAI (https://developers.openai.com/api/docs/guides/reasoning):
> «While reasoning tokens are not visible via the API, they still occupy space in the model's context window and are billed as output tokens.»

Количество видно в `usage.output_tokens_details.reasoning_tokens`, сам текст рассуждений скрыт. Это самая недоосвещённая причина перерасхода: невидимые токены тарифицируются по самой дорогой ставке (output).

## Retry: SDK повторяет запросы сам, по умолчанию

Официальный openai-python (https://github.com/openai/openai-python):
- по умолчанию **2 повтора**;
- дословно: «Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default».

**Следствие:** ретрай-цикл в коде приложения умножается на встроенные ретраи SDK. Но: при 429 и 5xx токены обычно не сгенерированы, значит и не тарифицированы. Утверждение «каждый повтор тарифицируется отдельно» — оверклейм. Реальный биллинговый риск — клиентский таймаут при уже сгенерированном ответе и агентные переспросы. **Citable-подтверждения по биллингу неуспешных запросов не найдено** (есть только треды на community.openai.com — по канону не источник). Формулировать осторожно или отправлять на сверку.

## Рыночная рамка: Gartner, июль 2026

Пресс-релиз «Gartner Forecasts Worldwide AI Platforms and Models Market to Grow 63% in 2026» (20.07.2026):
https://www.gartner.com/en/newsroom/press-releases/2026-07-20-gartner-forecasts-worldwide-ai-platforms-and-models-market-to-grow-63-percent-in-2026

- рынок AI-платформ и моделей: **$39 млрд в 2025 → $64 млрд в 2026, +63,4%**;
- расходы именно на GenAI-модели: **+117%**;
- DSLM: +210%.

Цитаты Arunasree Cheparthi, principal analyst Gartner — прямо про тезис статьи:
> «Enterprise AI budgets are coming under greater scrutiny, with increased focus on usage efficiency, cost control and measurable outcomes»
> «As usage-based pricing becomes harder to predict, buyers will turn to platforms that help them choose the right tools, monitor performance, enforce policy and keep costs under control»

Другие релизы Gartner 2026 (на случай нужды в рамке общих расходов): AI-расходы $2,5 трлн в 2026 (15.01.2026), AI-оптимизированная IaaS +96% (10.08.2026).

## Чего нет и придумывать нельзя

- рублёвых сумм «типичный счёт корпорации за LLM API» — данных нет;
- доли компаний, у которых счёт за LLM превысил план — не подтверждено;
- подтверждения тарификации неуспешных запросов из первичного источника — нет;
- цифры «скрытые расходы добавляют 30–100%», «reasoning-модель генерирует 20–40 тыс. невидимых токенов», «дешёвая модель обходится в 6 раз дороже в 21,8% случаев» — это из статьи на Хабре без атрибуции, **не переносить**.

## Строки для индекса

Цены за 1M токенов: Claude Opus 5 $5/$25 (×5), Sonnet 5 $2/$10 (×5, вводная до 31.08.2026), Haiku 4.5 $1/$5 (×5) → platform.claude.com/docs/pricing
gpt-5.6-sol $2,50/$15 (×6), gpt-5.6-luna $0,10/$0,60 (×6); разрыв sol/luna 25× → developers.openai.com/pricing
Кеширование Anthropic: чтение 0,1× input, запись 1,25× (5 мин), минимум 512–4096 токенов → platform.claude.com/prompt-caching
Кеширование OpenAI: чтение 10× дешевле, запись 1,25×, минимум 1024 токена, TTL 30 минут → developers.openai.com/prompt-caching
Reasoning-токены не видны через API, тарифицируются как output → developers.openai.com/reasoning
Рынок AI-платформ и моделей: $39 млрд (2025) → $64 млрд (2026), +63,4%; расходы на GenAI-модели +117% → Gartner, 20.07.2026
