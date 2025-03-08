# ChapaBot 🤖

Um bot do Discord moderno que integra com modelos de IA da Groq e OpenAI para fornecer respostas inteligentes em conversas.

## 📋 Características

- ✨ Integração com a API da Groq como serviço principal
- 🔄 Fallback automático para OpenAI quando necessário
- 💬 Mantém contexto das últimas 50 mensagens
- ⚡ Comandos slash (/) para melhor interação
- 🔒 Gerenciamento seguro de credenciais
- 📊 Sistema de logging para monitoramento

## 🛠️ Tecnologias

- [Python 3.8+](https://www.python.org/)
- [discord.py](https://discordpy.readthedocs.io/) - API do Discord
- [Groq API](https://groq.com/) - Modelo de IA primário
- [OpenAI API](https://openai.com/) - Modelo de IA secundário (fallback)

## 🚀 Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/botdiscordchatgpt.git
   cd botdiscordchatgpt
   ```

2. Crie um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -e .
   ```

4. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione suas chaves de API:
     ```
     DISCORD_TOKEN=seu_token_do_discord
     GROQ_API_KEY=sua_chave_da_groq
     OPENAI_API_KEY=sua_chave_da_openai
     ```

## ⚙️ Configuração do Bot Discord

1. Acesse o [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá para a seção "Bot" e clique em "Add Bot"
4. Habilite as "Privileged Gateway Intents":
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
5. Copie o token do bot e adicione ao seu arquivo `.env`
6. Use o link de convite gerado para adicionar o bot ao seu servidor

## 🎮 Uso

1. Inicie o bot:

   ```bash
   python -m src.main
   ```

2. No Discord, use os seguintes comandos:
   - `/ajuda` - Mostra a lista de comandos disponíveis
   - `/conversar [mensagem]` - Inicia uma conversa com o bot
   - `/limpar` - Limpa o contexto da conversa atual
   - `/config` - Configura preferências do bot

## 🧩 Estrutura do Projeto
