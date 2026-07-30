-- Données de démarrage vérifiées manuellement le 2026-07-28 (tags et licences ajoutés le 2026-07-29).
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

INSERT OR IGNORE INTO tags (slug, name) VALUES
    ('chat', 'Chat'),
    ('code', 'Code'),
    ('ide-integration', 'Intégration IDE'),
    ('image-generation', 'Génération d''images'),
    ('video-generation', 'Génération vidéo'),
    ('voice-synthesis', 'Synthèse vocale'),
    ('workflow-automation', 'Automatisation de flux'),
    ('local-inference', 'Inférence locale'),
    ('open-weights', 'Poids ouverts'),
    ('multimodal', 'Multimodal'),
    ('model-hub', 'Hub de modèles');

INSERT OR IGNORE INTO item_tags (item_id, tag_id)
SELECT item.id, tag.id FROM catalog_items AS item CROSS JOIN tags AS tag
WHERE (item.slug IN ('chatgpt', 'gemini') AND tag.slug = 'multimodal')
   OR (item.slug IN ('chatgpt', 'claude', 'gemini', 'microsoft-copilot', 'le-chat', 'perplexity') AND tag.slug = 'chat')
   OR (item.slug IN ('claude', 'microsoft-copilot', 'github-copilot', 'cursor', 'continue') AND tag.slug = 'code')
   OR (item.slug IN ('github-copilot', 'cursor', 'continue') AND tag.slug = 'ide-integration')
   OR (item.slug IN ('ollama', 'hugging-face-hub', 'continue') AND tag.slug = 'open-weights')
   OR (item.slug IN ('ollama', 'continue', 'stable-diffusion', 'flux', 'n8n') AND tag.slug = 'local-inference')
   OR (item.slug IN ('ollama', 'hugging-face-hub') AND tag.slug = 'model-hub')
   OR (item.slug IN ('stable-diffusion', 'flux') AND tag.slug = 'image-generation')
   OR (item.slug = 'runway' AND tag.slug = 'video-generation')
   OR (item.slug = 'elevenlabs' AND tag.slug = 'voice-synthesis')
   OR (item.slug = 'n8n' AND tag.slug = 'workflow-automation');

INSERT OR IGNORE INTO licenses (name, spdx_id, url) VALUES
    ('MIT License', 'MIT', 'https://opensource.org/licenses/MIT'),
    ('Apache License 2.0', 'Apache-2.0', 'https://www.apache.org/licenses/LICENSE-2.0'),
    ('CreativeML Open RAIL-M', NULL, 'https://huggingface.co/spaces/CompVis/stable-diffusion-license');

INSERT OR IGNORE INTO item_licenses (item_id, license_id)
SELECT item.id, license.id FROM catalog_items AS item CROSS JOIN licenses AS license
WHERE (item.slug = 'ollama' AND license.spdx_id = 'MIT')
   OR (item.slug IN ('continue', 'hugging-face-hub') AND license.spdx_id = 'Apache-2.0')
   OR (item.slug = 'stable-diffusion' AND license.name = 'CreativeML Open RAIL-M');

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

-- Extension du catalogue vérifiée manuellement le 2026-07-29 : URLs officielles
-- contrôlées une à une (réponse HTTP directe ou blocage anti-bot connu sur un
-- domaine reconnu). Complète la sélection initiale avec la génération
-- d'images/musique/vidéo, l'écriture assistée, les assistants génériques
-- supplémentaires, l'hébergement de modèles et l'automatisation.

INSERT OR IGNORE INTO categories (slug, name, description) VALUES
    ('musique', 'Musique', 'Génération et édition musicale.'),
    ('ecriture', 'Écriture et productivité', 'Correction, reformulation et assistance rédactionnelle.'),
    ('design', 'Design', 'Création graphique et visuelle assistée par IA.'),
    ('traduction', 'Traduction', 'Traduction automatique.'),
    ('hebergement-modeles', 'Hébergement de modèles', 'Exécution de modèles IA via API hébergée.');

INSERT OR IGNORE INTO companies (name, website_url, country_code) VALUES
    ('Midjourney, Inc.', 'https://www.midjourney.com', 'US'),
    ('Leonardo AI', 'https://leonardo.ai', 'AU'),
    ('Ideogram AI', 'https://ideogram.ai', 'US'),
    ('Suno', 'https://suno.com', 'US'),
    ('Udio', 'https://www.udio.com', 'US'),
    ('Luma AI', 'https://lumalabs.ai', 'US'),
    ('Pika', 'https://pika.art', 'US'),
    ('Synthesia', 'https://www.synthesia.io', 'GB'),
    ('HeyGen', 'https://www.heygen.com', 'US'),
    ('Descript', 'https://www.descript.com', 'US'),
    ('Notion Labs', 'https://www.notion.com', 'US'),
    ('Grammarly', 'https://www.grammarly.com', 'US'),
    ('Jasper', 'https://www.jasper.ai', 'US'),
    ('Character Technologies', 'https://character.ai', 'US'),
    ('Quora', 'https://poe.com', 'US'),
    ('You.com', 'https://you.com', 'US'),
    ('Cognition AI', 'https://windsurf.com', 'US'),
    ('Tabnine', 'https://www.tabnine.com', 'IL'),
    ('Sourcegraph', 'https://sourcegraph.com', 'US'),
    ('LM Studio', 'https://lmstudio.ai', 'US'),
    ('Jan', 'https://jan.ai', 'SG'),
    ('LangChain', 'https://www.langchain.com', 'US'),
    ('Zapier', 'https://zapier.com', 'US'),
    ('DeepL SE', 'https://www.deepl.com', 'DE'),
    ('Adobe', 'https://firefly.adobe.com', 'US'),
    ('Meta Platforms', 'https://www.meta.ai', 'US'),
    ('xAI', 'https://grok.com', 'US'),
    ('DeepSeek', 'https://chat.deepseek.com', 'CN'),
    ('Replicate', 'https://replicate.com', 'US'),
    ('Together AI', 'https://www.together.ai', 'US'),
    ('Groq', 'https://groq.com', 'US'),
    ('Vercel', 'https://v0.app', 'US'),
    ('StackBlitz', 'https://bolt.new', 'US');

INSERT OR IGNORE INTO catalog_items (slug, name, item_type, description, official_url, company_id, api_available, works_offline, is_open_source) VALUES
    ('midjourney', 'Midjourney', 'service', 'Génération d''images à partir de texte, principalement via Discord et une interface web.', 'https://www.midjourney.com', (SELECT id FROM companies WHERE name = 'Midjourney, Inc.'), 0, 0, 0),
    ('dall-e', 'DALL·E', 'service', 'Génération d''images à partir de texte, intégrée à ChatGPT et à l''API OpenAI.', 'https://openai.com/index/dall-e-3/', (SELECT id FROM companies WHERE name = 'OpenAI'), 1, 0, 0),
    ('leonardo-ai', 'Leonardo.Ai', 'service', 'Génération et édition d''images, orientée jeux vidéo et design.', 'https://leonardo.ai', (SELECT id FROM companies WHERE name = 'Leonardo AI'), 1, 0, 0),
    ('ideogram', 'Ideogram', 'service', 'Génération d''images avec un bon rendu de texte intégré à l''image.', 'https://ideogram.ai', (SELECT id FROM companies WHERE name = 'Ideogram AI'), 1, 0, 0),
    ('suno', 'Suno', 'service', 'Génération de musique et de chansons à partir de texte.', 'https://suno.com', (SELECT id FROM companies WHERE name = 'Suno'), 0, 0, 0),
    ('udio', 'Udio', 'service', 'Génération de musique à partir de texte.', 'https://www.udio.com', (SELECT id FROM companies WHERE name = 'Udio'), 0, 0, 0),
    ('luma-dream-machine', 'Luma Dream Machine', 'service', 'Génération de vidéos à partir de texte ou d''images.', 'https://lumalabs.ai', (SELECT id FROM companies WHERE name = 'Luma AI'), 1, 0, 0),
    ('pika', 'Pika', 'service', 'Génération et édition de vidéos à partir de texte ou d''images.', 'https://pika.art', (SELECT id FROM companies WHERE name = 'Pika'), 0, 0, 0),
    ('synthesia', 'Synthesia', 'service', 'Génération de vidéos avec avatars IA parlants.', 'https://www.synthesia.io', (SELECT id FROM companies WHERE name = 'Synthesia'), 1, 0, 0),
    ('heygen', 'HeyGen', 'service', 'Génération de vidéos avec avatars IA et doublage.', 'https://www.heygen.com', (SELECT id FROM companies WHERE name = 'HeyGen'), 1, 0, 0),
    ('descript', 'Descript', 'tool', 'Édition de texte, audio et vidéo assistée par IA.', 'https://www.descript.com', (SELECT id FROM companies WHERE name = 'Descript'), 0, 0, 0),
    ('notion-ai', 'Notion AI', 'service', 'Assistant d''écriture et de résumé intégré à Notion.', 'https://www.notion.com/product/ai', (SELECT id FROM companies WHERE name = 'Notion Labs'), 0, 0, 0),
    ('grammarly', 'Grammarly', 'tool', 'Correction, reformulation et assistance à l''écriture.', 'https://www.grammarly.com', (SELECT id FROM companies WHERE name = 'Grammarly'), 0, 0, 0),
    ('jasper', 'Jasper', 'service', 'Assistant de rédaction pour le marketing et le contenu.', 'https://www.jasper.ai', (SELECT id FROM companies WHERE name = 'Jasper'), 1, 0, 0),
    ('character-ai', 'Character.AI', 'service', 'Conversations avec des personnages IA personnalisables.', 'https://character.ai', (SELECT id FROM companies WHERE name = 'Character Technologies'), 0, 0, 0),
    ('poe', 'Poe', 'service', 'Plateforme d''accès à plusieurs assistants IA et bots tiers.', 'https://poe.com', (SELECT id FROM companies WHERE name = 'Quora'), 1, 0, 0),
    ('you-com', 'You.com', 'service', 'Moteur de recherche et assistant IA combinés.', 'https://you.com', (SELECT id FROM companies WHERE name = 'You.com'), 1, 0, 0),
    ('windsurf', 'Windsurf', 'tool', 'Éditeur de code assisté par IA (agent de codage), racheté par Cognition (Devin).', 'https://windsurf.com', (SELECT id FROM companies WHERE name = 'Cognition AI'), 0, 0, 0),
    ('tabnine', 'Tabnine', 'tool', 'Complétion de code assistée par IA, avec option d''exécution privée pour les entreprises.', 'https://www.tabnine.com', (SELECT id FROM companies WHERE name = 'Tabnine'), 0, 0, 0),
    ('cody', 'Cody', 'tool', 'Assistant de code IA de Sourcegraph, avec recherche de code.', 'https://sourcegraph.com/cody', (SELECT id FROM companies WHERE name = 'Sourcegraph'), 0, 0, 0),
    ('lm-studio', 'LM Studio', 'tool', 'Application de bureau pour exécuter des modèles de langage en local, avec serveur API compatible OpenAI.', 'https://lmstudio.ai', (SELECT id FROM companies WHERE name = 'LM Studio'), 1, 1, 0),
    ('jan', 'Jan', 'framework', 'Application open source pour exécuter des modèles de langage en local, avec serveur API compatible OpenAI.', 'https://jan.ai', (SELECT id FROM companies WHERE name = 'Jan'), 1, 1, 1),
    ('langchain', 'LangChain', 'framework', 'Bibliothèque open source pour construire des applications avec des modèles de langage.', 'https://www.langchain.com', (SELECT id FROM companies WHERE name = 'LangChain'), 1, 1, 1),
    ('zapier', 'Zapier', 'service', 'Automatisation de flux de travail, avec fonctionnalités IA (agents, recherche).', 'https://zapier.com', (SELECT id FROM companies WHERE name = 'Zapier'), 1, 0, 0),
    ('deepl', 'DeepL', 'service', 'Traduction automatique et écriture assistée par IA.', 'https://www.deepl.com', (SELECT id FROM companies WHERE name = 'DeepL SE'), 1, 0, 0),
    ('notebooklm', 'NotebookLM', 'service', 'Assistant de recherche et de synthèse basé sur les documents fournis par l''utilisateur.', 'https://notebooklm.google', (SELECT id FROM companies WHERE name = 'Google'), 0, 0, 0),
    ('adobe-firefly', 'Adobe Firefly', 'service', 'Génération et édition d''images et de designs, intégrée aux produits Adobe.', 'https://firefly.adobe.com', (SELECT id FROM companies WHERE name = 'Adobe'), 1, 0, 0),
    ('meta-ai', 'Meta AI', 'service', 'Assistant conversationnel de Meta, intégré à ses applications.', 'https://www.meta.ai', (SELECT id FROM companies WHERE name = 'Meta Platforms'), 0, 0, 0),
    ('grok', 'Grok', 'service', 'Assistant conversationnel de xAI, intégré à X (Twitter).', 'https://grok.com', (SELECT id FROM companies WHERE name = 'xAI'), 1, 0, 0),
    ('deepseek-chat', 'DeepSeek', 'service', 'Assistant conversationnel de DeepSeek, dont certains modèles sont aussi publiés en open weights.', 'https://chat.deepseek.com', (SELECT id FROM companies WHERE name = 'DeepSeek'), 1, 0, 0),
    ('replicate', 'Replicate', 'service', 'Plateforme d''hébergement et d''exécution de modèles IA via API.', 'https://replicate.com', (SELECT id FROM companies WHERE name = 'Replicate'), 1, 0, 0),
    ('together-ai', 'Together AI', 'service', 'Plateforme d''hébergement et d''inférence de modèles IA open source via API.', 'https://www.together.ai', (SELECT id FROM companies WHERE name = 'Together AI'), 1, 0, 0),
    ('groq', 'Groq', 'service', 'Plateforme d''inférence de modèles IA à très faible latence via API.', 'https://groq.com', (SELECT id FROM companies WHERE name = 'Groq'), 1, 0, 0),
    ('v0', 'v0', 'tool', 'Génération d''interfaces et de code par IA, développé par Vercel.', 'https://v0.app', (SELECT id FROM companies WHERE name = 'Vercel'), 1, 0, 0),
    ('bolt-new', 'Bolt.new', 'tool', 'Génération et exécution d''applications web complètes par IA dans le navigateur.', 'https://bolt.new', (SELECT id FROM companies WHERE name = 'StackBlitz'), 0, 0, 0);

INSERT OR IGNORE INTO item_categories (item_id, category_id)
SELECT item.id, category.id FROM catalog_items AS item CROSS JOIN categories AS category
WHERE (item.slug IN ('midjourney', 'dall-e', 'leonardo-ai', 'ideogram', 'adobe-firefly') AND category.slug = 'images')
   OR (item.slug IN ('midjourney', 'dall-e', 'leonardo-ai', 'ideogram', 'adobe-firefly') AND category.slug = 'design')
   OR (item.slug IN ('suno', 'udio') AND category.slug = 'musique')
   OR (item.slug IN ('luma-dream-machine', 'pika', 'synthesia', 'heygen') AND category.slug = 'video')
   OR (item.slug IN ('descript', 'heygen') AND category.slug = 'voix-audio')
   OR (item.slug IN ('notion-ai', 'grammarly', 'jasper') AND category.slug = 'ecriture')
   OR (item.slug IN ('character-ai', 'poe', 'you-com', 'meta-ai', 'grok', 'deepseek-chat', 'notebooklm') AND category.slug = 'assistant-generaliste')
   OR (item.slug IN ('you-com', 'notebooklm') AND category.slug = 'recherche')
   OR (item.slug IN ('windsurf', 'tabnine', 'cody', 'v0', 'bolt-new', 'langchain') AND category.slug = 'programmation')
   OR (item.slug IN ('lm-studio', 'jan', 'langchain') AND category.slug = 'local')
   OR (item.slug IN ('lm-studio', 'jan', 'langchain', 'replicate', 'together-ai', 'groq', 'deepseek-chat') AND category.slug = 'modeles-ia')
   OR (item.slug = 'zapier' AND category.slug = 'automatisation')
   OR (item.slug = 'deepl' AND category.slug = 'traduction')
   OR (item.slug IN ('replicate', 'together-ai', 'groq') AND category.slug = 'hebergement-modeles');

INSERT OR IGNORE INTO item_platforms (item_id, platform_id)
SELECT item.id, platform.id FROM catalog_items AS item CROSS JOIN platforms AS platform
WHERE (item.slug IN (
        'midjourney', 'dall-e', 'leonardo-ai', 'ideogram', 'suno', 'udio', 'luma-dream-machine',
        'pika', 'synthesia', 'heygen', 'descript', 'notion-ai', 'grammarly', 'jasper',
        'character-ai', 'poe', 'you-com', 'windsurf', 'tabnine', 'cody', 'zapier', 'deepl',
        'notebooklm', 'adobe-firefly', 'meta-ai', 'grok', 'deepseek-chat', 'replicate',
        'together-ai', 'groq', 'v0', 'bolt-new'
      ) AND platform.slug = 'web')
   OR (item.slug IN ('lm-studio', 'jan', 'descript') AND platform.slug IN ('windows', 'macos', 'linux'))
   OR (item.slug IN (
        'dall-e', 'leonardo-ai', 'ideogram', 'luma-dream-machine', 'synthesia', 'heygen', 'jasper',
        'poe', 'you-com', 'lm-studio', 'jan', 'langchain', 'zapier', 'deepl', 'adobe-firefly', 'grok',
        'deepseek-chat', 'replicate', 'together-ai', 'groq', 'v0'
      ) AND platform.slug = 'api');

INSERT OR IGNORE INTO item_tags (item_id, tag_id)
SELECT item.id, tag.id FROM catalog_items AS item CROSS JOIN tags AS tag
WHERE (item.slug IN ('midjourney', 'dall-e', 'leonardo-ai', 'ideogram', 'adobe-firefly') AND tag.slug = 'image-generation')
   OR (item.slug IN ('luma-dream-machine', 'pika', 'synthesia', 'heygen') AND tag.slug = 'video-generation')
   OR (item.slug IN ('descript', 'heygen') AND tag.slug = 'voice-synthesis')
   OR (item.slug IN ('character-ai', 'poe', 'you-com', 'meta-ai', 'grok', 'deepseek-chat') AND tag.slug = 'chat')
   OR (item.slug IN ('windsurf', 'tabnine', 'cody', 'v0', 'bolt-new') AND tag.slug = 'code')
   OR (item.slug IN ('windsurf', 'tabnine', 'cody') AND tag.slug = 'ide-integration')
   OR (item.slug IN ('lm-studio', 'jan', 'langchain') AND tag.slug = 'local-inference')
   OR (item.slug IN ('jan', 'langchain') AND tag.slug = 'open-weights')
   OR (item.slug IN ('replicate', 'together-ai', 'groq') AND tag.slug = 'model-hub')
   OR (item.slug = 'zapier' AND tag.slug = 'workflow-automation');

INSERT OR IGNORE INTO item_licenses (item_id, license_id)
SELECT item.id, license.id FROM catalog_items AS item CROSS JOIN licenses AS license
WHERE (item.slug IN ('jan', 'langchain') AND license.spdx_id = 'MIT');

INSERT OR IGNORE INTO sources (slug, name, base_url, license_note)
SELECT 'manuel-' || slug, name || ' (fiche manuelle)', official_url,
       'Fiche ajoutée manuellement le 2026-07-29, URL officielle vérifiée directement.'
FROM catalog_items
WHERE slug IN (
    'midjourney', 'dall-e', 'leonardo-ai', 'ideogram', 'suno', 'udio', 'luma-dream-machine',
    'pika', 'synthesia', 'heygen', 'descript', 'notion-ai', 'grammarly', 'jasper',
    'character-ai', 'poe', 'you-com', 'windsurf', 'tabnine', 'cody', 'lm-studio', 'jan',
    'langchain', 'zapier', 'deepl', 'notebooklm', 'adobe-firefly', 'meta-ai', 'grok',
    'deepseek-chat', 'replicate', 'together-ai', 'groq', 'v0', 'bolt-new'
);

INSERT OR IGNORE INTO source_records (source_id, item_id, external_id, source_url)
SELECT source.id, item.id, item.slug, item.official_url
FROM catalog_items AS item
JOIN sources AS source ON source.slug = 'manuel-' || item.slug;
