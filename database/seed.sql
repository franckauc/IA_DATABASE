-- Données de démarrage vérifiées manuellement le 2026-07-28.
-- Les collecteurs automatiques devront remplacer ou compléter ces fiches
-- en conservant leur provenance dans sources et source_records.

INSERT OR IGNORE INTO categories (slug, name, description) VALUES
    ('assistant-generaliste', 'Assistant généraliste', 'Conversation, rédaction, analyse et tâches quotidiennes.'),
    ('programmation', 'Programmation', 'Aide au développement logiciel.'),
    ('modeles-ia', 'Modèles IA', 'Modèles de langage, image, audio et leurs écosystèmes.'),
    ('local', 'IA locale', 'Exécution possible sur le matériel de l''utilisateur.'),
    ('images', 'Images', 'Génération ou transformation d''images.'),
    ('video', 'Vidéo', 'Génération, édition ou effets vidéo.'),
    ('voix-audio', 'Voix et audio', 'Synthèse, traitement et transcription audio.'),
    ('recherche', 'Recherche', 'Recherche web, documentaire ou scientifique.'),
    ('automatisation', 'Automatisation', 'Automatisation de processus et agents.'),
    ('developpement-web', 'Développement web', 'Création de sites et applications web.');

INSERT OR IGNORE INTO platforms (slug, name) VALUES
    ('web', 'Web'),
    ('windows', 'Windows'),
    ('macos', 'macOS'),
    ('linux', 'Linux'),
    ('android', 'Android'),
    ('ios', 'iOS'),
    ('api', 'API');

INSERT OR IGNORE INTO companies (name, website_url, country_code) VALUES
    ('OpenAI', 'https://openai.com', 'US'),
    ('Anthropic', 'https://www.anthropic.com', 'US'),
    ('Google', 'https://ai.google', 'US'),
    ('Microsoft', 'https://www.microsoft.com', 'US'),
    ('Mistral AI', 'https://mistral.ai', 'FR'),
    ('Perplexity AI', 'https://www.perplexity.ai', 'US'),
    ('Ollama', 'https://ollama.com', 'US'),
    ('Hugging Face', 'https://huggingface.co', 'US'),
    ('GitHub', 'https://github.com', 'US'),
    ('Anysphere', 'https://www.anysphere.inc', 'US'),
    ('Continue', 'https://www.continue.dev', 'US'),
    ('Stability AI', 'https://stability.ai', 'GB'),
    ('Black Forest Labs', 'https://blackforestlabs.ai', 'DE'),
    ('Runway', 'https://runwayml.com', 'US'),
    ('ElevenLabs', 'https://elevenlabs.io', 'US'),
    ('n8n', 'https://n8n.io', 'DE');

INSERT OR IGNORE INTO sources (slug, name, base_url, terms_url, license_note) VALUES
    ('openai-chatgpt', 'OpenAI — ChatGPT', 'https://chatgpt.com', 'https://openai.com/policies/terms-of-use/', 'Fiche initiale depuis le site officiel.'),
    ('anthropic-claude', 'Anthropic — Claude', 'https://claude.ai', 'https://www.anthropic.com/legal/consumer-terms', 'Fiche initiale depuis le site officiel.'),
    ('google-gemini', 'Google — Gemini', 'https://gemini.google.com', 'https://policies.google.com/terms', 'Fiche initiale depuis le site officiel.'),
    ('microsoft-copilot', 'Microsoft — Copilot', 'https://copilot.microsoft.com', 'https://www.microsoft.com/servicesagreement', 'Fiche initiale depuis le site officiel.'),
    ('mistral-le-chat', 'Mistral AI — Le Chat', 'https://chat.mistral.ai', 'https://mistral.ai/terms/', 'Fiche initiale depuis le site officiel.'),
    ('perplexity', 'Perplexity', 'https://www.perplexity.ai', 'https://www.perplexity.ai/hub/legal/terms-of-service', 'Fiche initiale depuis le site officiel.'),
    ('ollama', 'Ollama', 'https://ollama.com', 'https://ollama.com/terms', 'Fiche initiale depuis le site officiel.'),
    ('hugging-face', 'Hugging Face', 'https://huggingface.co', 'https://huggingface.co/terms-of-service', 'Fiche initiale depuis le site officiel.'),
    ('github-copilot', 'GitHub Copilot', 'https://github.com/features/copilot', 'https://docs.github.com/site-policy/github-terms/github-terms-of-service', 'Fiche initiale depuis le site officiel.'),
    ('cursor', 'Cursor', 'https://www.cursor.com', 'https://www.cursor.com/terms-of-service', 'Fiche initiale depuis le site officiel.'),
    ('continue', 'Continue', 'https://www.continue.dev', 'https://www.continue.dev/terms', 'Fiche initiale depuis le site officiel.'),
    ('stability-ai', 'Stability AI', 'https://stability.ai', 'https://stability.ai/terms-of-service', 'Fiche initiale depuis le site officiel.'),
    ('black-forest-labs', 'Black Forest Labs', 'https://blackforestlabs.ai', 'https://blackforestlabs.ai/terms', 'Fiche initiale depuis le site officiel.'),
    ('runway', 'Runway', 'https://runwayml.com', 'https://runwayml.com/terms-of-use', 'Fiche initiale depuis le site officiel.'),
    ('elevenlabs', 'ElevenLabs', 'https://elevenlabs.io', 'https://elevenlabs.io/terms', 'Fiche initiale depuis le site officiel.'),
    ('n8n', 'n8n', 'https://n8n.io', 'https://n8n.io/legal/terms', 'Fiche initiale depuis le site officiel.');

INSERT OR IGNORE INTO catalog_items (slug, name, item_type, description, official_url, documentation_url, company_id, api_available, works_offline, is_open_source) VALUES
    ('chatgpt', 'ChatGPT', 'service', 'Assistant conversationnel pour la rédaction, l''analyse, le code et les tâches quotidiennes.', 'https://chatgpt.com', 'https://help.openai.com/en/collections/3742473-chatgpt', (SELECT id FROM companies WHERE name = 'OpenAI'), 1, 0, 0),
    ('claude', 'Claude', 'service', 'Assistant conversationnel et outil d''analyse proposé par Anthropic.', 'https://claude.ai', 'https://docs.anthropic.com', (SELECT id FROM companies WHERE name = 'Anthropic'), 1, 0, 0),
    ('gemini', 'Gemini', 'service', 'Assistant IA de Google.', 'https://gemini.google.com', 'https://ai.google.dev/gemini-api/docs', (SELECT id FROM companies WHERE name = 'Google'), 1, 0, 0),
    ('microsoft-copilot', 'Microsoft Copilot', 'service', 'Assistant IA de Microsoft disponible sur le web et dans ses produits.', 'https://copilot.microsoft.com', 'https://support.microsoft.com/copilot', (SELECT id FROM companies WHERE name = 'Microsoft'), 1, 0, 0),
    ('le-chat', 'Le Chat', 'service', 'Assistant conversationnel de Mistral AI.', 'https://chat.mistral.ai', 'https://docs.mistral.ai', (SELECT id FROM companies WHERE name = 'Mistral AI'), 1, 0, 0),
    ('perplexity', 'Perplexity', 'service', 'Moteur de réponse et de recherche assisté par IA.', 'https://www.perplexity.ai', 'https://docs.perplexity.ai', (SELECT id FROM companies WHERE name = 'Perplexity AI'), 1, 0, 0),
    ('ollama', 'Ollama', 'framework', 'Outil pour exécuter et servir des modèles localement.', 'https://ollama.com', 'https://docs.ollama.com', (SELECT id FROM companies WHERE name = 'Ollama'), 1, 1, 1),
    ('hugging-face-hub', 'Hugging Face Hub', 'service', 'Plateforme de partage de modèles, jeux de données et démonstrations IA.', 'https://huggingface.co', 'https://huggingface.co/docs/hub', (SELECT id FROM companies WHERE name = 'Hugging Face'), 1, 0, 1),
    ('github-copilot', 'GitHub Copilot', 'service', 'Assistant de programmation de GitHub.', 'https://github.com/features/copilot', 'https://docs.github.com/copilot', (SELECT id FROM companies WHERE name = 'GitHub'), 1, 0, 0),
    ('cursor', 'Cursor', 'tool', 'Éditeur de code assisté par IA.', 'https://www.cursor.com', 'https://docs.cursor.com', (SELECT id FROM companies WHERE name = 'Anysphere'), 0, 0, 0),
    ('continue', 'Continue', 'framework', 'Assistant de code open source pour IDE et terminal.', 'https://www.continue.dev', 'https://docs.continue.dev', (SELECT id FROM companies WHERE name = 'Continue'), 1, 1, 1),
    ('stable-diffusion', 'Stable Diffusion', 'model', 'Famille de modèles de génération et transformation d''images.', 'https://stability.ai/stable-diffusion', 'https://platform.stability.ai/docs', (SELECT id FROM companies WHERE name = 'Stability AI'), 1, 1, 0),
    ('flux', 'FLUX', 'model', 'Famille de modèles de génération d''images de Black Forest Labs.', 'https://blackforestlabs.ai', 'https://docs.bfl.ai', (SELECT id FROM companies WHERE name = 'Black Forest Labs'), 1, 1, 0),
    ('runway', 'Runway', 'service', 'Outils de création et génération vidéo.', 'https://runwayml.com', 'https://help.runwayml.com', (SELECT id FROM companies WHERE name = 'Runway'), 1, 0, 0),
    ('elevenlabs', 'ElevenLabs', 'service', 'Outils de synthèse et de traitement vocal.', 'https://elevenlabs.io', 'https://elevenlabs.io/docs', (SELECT id FROM companies WHERE name = 'ElevenLabs'), 1, 0, 0),
    ('n8n', 'n8n', 'framework', 'Plateforme d''automatisation de flux de travail.', 'https://n8n.io', 'https://docs.n8n.io', (SELECT id FROM companies WHERE name = 'n8n'), 1, 1, 0);

INSERT OR IGNORE INTO item_categories (item_id, category_id)
SELECT item.id, category.id FROM catalog_items AS item CROSS JOIN categories AS category
WHERE (item.slug IN ('chatgpt', 'claude', 'gemini', 'microsoft-copilot', 'le-chat') AND category.slug = 'assistant-generaliste')
   OR (item.slug IN ('github-copilot', 'cursor', 'continue') AND category.slug = 'programmation')
   OR (item.slug IN ('ollama', 'hugging-face-hub', 'stable-diffusion', 'flux') AND category.slug = 'modeles-ia')
   OR (item.slug IN ('ollama', 'continue', 'stable-diffusion', 'flux', 'n8n') AND category.slug = 'local')
   OR (item.slug IN ('stable-diffusion', 'flux') AND category.slug = 'images')
   OR (item.slug = 'runway' AND category.slug = 'video')
   OR (item.slug = 'elevenlabs' AND category.slug = 'voix-audio')
   OR (item.slug = 'perplexity' AND category.slug = 'recherche')
   OR (item.slug = 'n8n' AND category.slug = 'automatisation');

INSERT OR IGNORE INTO item_platforms (item_id, platform_id)
SELECT item.id, platform.id FROM catalog_items AS item CROSS JOIN platforms AS platform
WHERE (item.slug IN ('chatgpt', 'claude', 'gemini', 'microsoft-copilot', 'le-chat', 'perplexity', 'hugging-face-hub', 'github-copilot', 'cursor', 'runway', 'elevenlabs', 'n8n') AND platform.slug = 'web')
   OR (item.slug IN ('ollama', 'continue', 'stable-diffusion', 'flux') AND platform.slug IN ('windows', 'macos', 'linux'))
   OR (item.api_available = 1 AND platform.slug = 'api');

INSERT OR IGNORE INTO source_records (source_id, item_id, external_id, source_url)
SELECT source.id, item.id, item.slug, item.official_url
FROM catalog_items AS item
JOIN sources AS source ON source.slug = CASE item.slug
    WHEN 'chatgpt' THEN 'openai-chatgpt'
    WHEN 'claude' THEN 'anthropic-claude'
    WHEN 'gemini' THEN 'google-gemini'
    WHEN 'microsoft-copilot' THEN 'microsoft-copilot'
    WHEN 'le-chat' THEN 'mistral-le-chat'
    WHEN 'perplexity' THEN 'perplexity'
    WHEN 'ollama' THEN 'ollama'
    WHEN 'hugging-face-hub' THEN 'hugging-face'
    WHEN 'github-copilot' THEN 'github-copilot'
    WHEN 'cursor' THEN 'cursor'
    WHEN 'continue' THEN 'continue'
    WHEN 'stable-diffusion' THEN 'stability-ai'
    WHEN 'flux' THEN 'black-forest-labs'
    WHEN 'runway' THEN 'runway'
    WHEN 'elevenlabs' THEN 'elevenlabs'
    WHEN 'n8n' THEN 'n8n'
END;
