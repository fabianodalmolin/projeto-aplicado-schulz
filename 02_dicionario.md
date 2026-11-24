# Dicionário de Dados do Sistema - Modelo Unificado (3 Entidades)

## 1. Tabela: tecnico_solicitante
Armazena os dados dos metrologistas e operadores do laboratório.

*   `id_tecnico`: Inteiro (INTEGER) | Chave Primária (PK) com Auto-incremento.
*   `nome_metrologista`: Texto (VARCHAR) | Nome completo do metrologista.
*   `matricula`: Texto (VARCHAR) | Registro do Empregado (RE) na Schulz.

## 2. Tabela: equipamento
Centraliza as informações cadastrais e de vigência dos instrumentos e padrões.

*   `id_equipamento`: Inteiro (INTEGER) | Chave Primária (PK) com Auto-incremento.
*   `codigo_tag`: Texto (VARCHAR) | Código patrimonial único do ativo (Ex: 500.011).
*   `denominacao`: Texto (VARCHAR) | Tipo do equipamento (Ex: Máquina MMC).
*   `fabricante`: Texto (VARCHAR) | Fabricante do instrumento (Ex: Carl Zeiss).
*   `data_proxima_calibracao`: Data (DATE) | Trava de vigência anual da calibração.

## 3. Tabela: medicao
Registra o histórico metrológico, unificando os dados do Calypso com as chaves estrangeiras.

*   `id_medicao`: Inteiro (INTEGER) | Chave Primária (PK) com Auto-incremento.
*   `id_tecnico`: Inteiro (INTEGER) | Chave Estrangeira (FK) ligada à tabela tecnico_solicitante.
*   `id_equipamento`: Inteiro (INTEGER) | Chave Estrangeira (FK) ligada à tabela equipamento.
*   `measurement_plan`: Texto (VARCHAR) | Nome do plano de medição (Ex: 703.1208_TESTE).
*   `part_number`: Texto (VARCHAR) | Identificador da peça física ou lote (Ex: Peça 27).
*   `nome_caracteristica`: Texto (VARCHAR) | Cota geométrica avaliada (Ex: PLANICIDADE_REF).
*   `valor_nominal`: Real (NUMERIC) | Valor ideal definido pela engenharia.
*   `tolerancia_superior`: Real (NUMERIC) | Limite máximo aceitável.
*   `tolerancia_inferior`: Real (NUMERIC) | Limite mínimo aceitável.
*   `valor_obtido_media`: Real (NUMERIC) | Média calculada das medições (Actual).
*   `status_aprovacao`: Texto (VARCHAR) | Status final gravado automaticamente ('Apr' ou 'Rep').
