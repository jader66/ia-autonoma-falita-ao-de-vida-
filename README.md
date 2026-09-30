# Assistente de IA — V1

Assistente pessoal para Windows com uma única tela central.

## Conceito

Todas as funções são acessadas pela mesma conversa. O usuário não precisa navegar entre abas para executar tarefas.

A interface é apenas a central do assistente; arquivos, Windows, internet, tarefas, memória e automações ficam nos módulos internos.

## V1

- Interface única em português.
- Comandos por texto.
- Respostas na própria tela.
- Abertura de programas e sites.
- Comandos básicos do Windows.
- Criação de lembretes simples.
- Histórico da sessão.
- Resposta por voz preparada.
- Captura de voz preparada sem PyAudio.
- Arquitetura modular.
- Tratamento de erros.

## Executar

Recomendado: Python 3.11 no Windows.

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Comandos de exemplo

- abrir calculadora
- abrir bloco de notas
- abrir navegador
- abrir youtube
- que horas são
- criar lembrete em 10 minutos de testar o sistema
- sair

O nome do assistente ainda não é definido nesta versão.
