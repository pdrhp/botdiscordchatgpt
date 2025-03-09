# Chapabot

Um bot do Discord moderno que integra com modelos de IA da Groq e OpenAI para fornecer respostas inteligentes em conversas.

## Características

- Integração com a API da Groq como serviço principal
- Fallback automático para OpenAI quando necessário
- Armazenamento de contexto das últimas 50 mensagens por canal
- Comandos tradicionais e slash (/) para melhor interação
- Personalidade customizável do bot
- Sistema de logging para monitoramento e diagnóstico
- Persistência de dados em SQLite
- Limpeza automática de dados antigos

## Tecnologias

- Python 3.8+
- discord.py - API do Discord
- Groq API - Modelo de IA primário
- OpenAI API - Modelo de IA secundário (fallback)
- SQLite - Armazenamento persistente de mensagens
- Pydantic - Validação de configurações
- Loguru - Sistema de logging avançado

## Requisitos

- Python 3.8 ou superior
- Token de bot do Discord
- Chave de API da Groq
- Chave de API da OpenAI (opcional, para fallback)
- Permissões de gateway privilegiadas no Discord (MESSAGE_CONTENT, SERVER_MEMBERS)

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/discord-ai-bot.git
   cd discord-ai-bot
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
     BOT_PERSONALITY=personalidade_customizada_do_bot
     ```

## Configuração do Bot Discord

1. Acesse o [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá para a seção "Bot" e clique em "Add Bot"
4. Habilite as "Privileged Gateway Intents":
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
5. Copie o token do bot e adicione ao seu arquivo `.env`
6. Use o link de convite gerado para adicionar o bot ao seu servidor

## Configuração Avançada

O bot utiliza um arquivo de configuração YAML para definir parâmetros avançados. Um arquivo de configuração padrão será criado automaticamente em `config/config.yaml` na primeira execução. Você pode editar este arquivo para personalizar:

- Prefixo de comando
- Modelo de IA padrão
- Número máximo de mensagens de contexto
- Nível de logging
- Timeout de resposta
- Número máximo de tokens
- Temperatura de geração de texto

## Uso

1. Inicie o bot:

   ```bash
   python -m src.main
   ```

2. No Discord, use os seguintes comandos:

   ### Comandos Tradicionais

   - `!ajuda` - Mostra a lista de comandos disponíveis
   - `!conversar [mensagem]` - Conversa com a IA
   - `!limpar` - Limpa o histórico de conversa do canal atual
   - `!personalidade` - Mostra a personalidade atual do bot
   - `!personalidade [nova]` - Altera a personalidade do bot (apenas administradores)

   ### Comandos Slash

   - `/conversar [mensagem]` - Conversa com a IA
   - `/limpar` - Limpa o histórico de conversa do canal atual
   - `/personalidade` - Mostra ou altera a personalidade do bot

   ### Menção

   - Você também pode mencionar o bot em qualquer mensagem para conversar com ele

## Estrutura do Projeto

```ascii
chapabot/
├── .env # Arquivo de variáveis de ambiente (não versionado)
├── .gitignore # Arquivos a serem ignorados pelo git
├── README.md # Documentação do projeto
├── requirements.txt # Dependências do projeto
├── pyproject.toml # Configuração do projeto
├── config/ # Diretório de configuração
│ └── config.yaml # Arquivo de configuração
├── data/ # Diretório de dados
│ └── messages.db # Banco de dados SQLite
├── logs/ # Diretório de logs
├── src/ # Código fonte
│ ├── init.py
│ ├── main.py # Ponto de entrada da aplicação
│ ├── bot/ # Módulo do bot
│ │ ├── init.py
│ │ ├── client.py # Cliente do Discord
│ │ └── commands.py # Comandos do bot
│ ├── ai/ # Módulo de IA
│ │ ├── init.py
│ │ ├── groq.py # Integração com Groq
│ │ ├── openai.py # Integração com OpenAI (fallback)
│ │ ├── personality.py # Gerenciamento de personalidade
│ │ ├── message_store.py # Armazenamento de mensagens
│ │ └── message_manager.py # Gerenciador de armazenamentos
│ └── utils/ # Utilitários
│ ├── init.py
│ ├── config.py # Configurações
│ └── logger.py # Logging
└── tests/ # Testes (opcional)
└── init.py
```

## Funcionalidades Detalhadas

### Sistema de Personalidade

O bot utiliza um sistema de personalidade que define como ele responde às mensagens. A personalidade é definida como um prompt de sistema que é enviado para o modelo de IA em cada interação. Você pode:

- Ver a personalidade atual com `!personalidade` ou `/personalidade`
- Alterar a personalidade com `!personalidade [nova]` ou `/personalidade [nova]` (apenas administradores)
- Definir uma personalidade padrão no arquivo `.env` com a variável `BOT_PERSONALITY`

### Armazenamento de Contexto

O bot mantém o contexto das últimas 50 mensagens (configurável) por canal, permitindo conversas mais coerentes. O contexto inclui:

- Mensagens dos usuários com seus nomes
- Respostas do bot
- Personalidade do bot como mensagem de sistema

### Persistência de Dados

As mensagens são armazenadas em um banco de dados SQLite para persistência entre reinicializações do bot. O sistema:

- Armazena mensagens por canal
- Limita o número de mensagens por canal
- Limpa automaticamente mensagens antigas
- Mantém metadados como ID do usuário, nome e timestamp

### Fallback Automático

Se a API da Groq falhar ou atingir limites de taxa, o bot automaticamente:

1. Registra o erro no log
2. Tenta usar a API da OpenAI como fallback
3. Notifica se ambas as APIs falharem

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
