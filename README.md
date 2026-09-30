# Assistente de IA — V1.3

Assistente pessoal para Windows com uma única tela central.

## Objetivo

Todas as funções são acessadas pela mesma conversa. Não existem abas separadas para cada função.

## V1.3 — executável único

- Interface central única.
- Comandos por texto e voz.
- Controle básico do Windows.
- Abertura de programas e sites.
- Pesquisa na internet.
- Lembretes.
- Palavra de ativação configurável, padrão: "assistente".
- Reconhecimento de voz em português sem PyAudio.
- Modelo de voz incluído no build do executável.
- Build com PyInstaller em modo `--onefile`.
- O usuário final recebe somente `Assistente.exe`.

## Como gerar

Para desenvolvimento, use Python 3.11 no Windows e execute:

```bat
setup.bat
gerar_exe.bat
```

O resultado será:

```
dist\Assistente.exe
```

Esse é o arquivo que deve ser distribuído ao usuário final. Ele não precisa instalar Python nem criar ambiente virtual.

## Build automático

O GitHub Actions também gera automaticamente o executável Windows quando há atualização na `main`. No GitHub, abra **Actions > Build Windows EXE** e baixe o artefato **Assistente-Windows**.

## Comandos de exemplo

- abrir calculadora
- abrir bloco de notas
- abrir navegador
- abrir youtube
- que horas são
- criar lembrete em 10 minutos de testar o sistema
- sair

O nome do assistente ainda não é fixo.
