# UNISENAI
## ANÁLISE E DESENVOLVIMENTO DE SISTEMAS / SEGURANÇA CIBERNÉTICA
### DISCIPLINA: PROJETO APLICADO 1

**Integrantes:**
- FABIANO DALMOLIN CARVALHO [1]
- FELIPE GABRIEL TEIXEIRA SANCHO [1]
- GABRIEL FERNANDO PEREIRA ARALDI [1]
- KAUAN GABRIEL DOS SANTOS ARISTIDES RAMALHO [2]
- ROBERTO BARROS GARCIA [2]

**Orientador:** PROF. MSc. HUGO MENEZES BARRA

**Desafio 2:** Modelagem e implementação de banco de dados  
*Florianópolis, SC — 2026*

---
[1] Aluno do curso de Análise e Desenvolvimento de Sistemas.  
[2] Aluno do curso de Segurança Cibernética.

---

## 1. INTRODUÇÃO E CONTEXTUALIZAÇÃO
Este documento apresenta a Entrega 02 do Projeto Aplicado I, cujo foco é a transição dos registros metrológicos manuais originados no software Zeiss Calypso para uma arquitetura relacional em SQLite. O objetivo primordial é garantir a integridade, o histórico de calibração e a eliminação de anomalias comuns identificadas em planilhas locais (como erros de macro e falhas de preenchimento).

## 2. LINK DO REPOSITÓRIO (GITHUB)
Os arquivos de codificação, dicionários e scripts encontram-se disponíveis em:
- **Link do Repositório:** [projeto-aplicado-schulz](https://github.com/fabianodalmolin/projeto-aplicado-schulz.git)

## 3. ORGANIZAÇÃO DOS DADOS (01_estrutura.md)
A modelagem conceitual do ecossistema de metrologia foi estruturada estritamente em 3 entidades principais:
- **Técnico / Solicitante (Metrologista):** Controla os dados de identificação dos operadores habilitados (RE/Matrícula e Nome).
- **Equipamento:** Centraliza os ativos tridimensionais (como as MMCs) e padrões laboratoriais, controlando seus fabricantes, números de série e datas críticas de vigência de calibração anual.
- **Medição:** Consolida todo o histórico metrológico dimensional, amarrando as especificações técnicas da engenharia (cotas, nominais, tolerâncias superiores/inferiores), as leituras obtidas nas duas passagens físicas da máquina e o respectivo status automatizado de aprovação ou reprovação.

A normalização rígida e a eliminação da duplicidade de dados reduzem drasticamente o espaço consumido em disco e blindam o backend contra distorções matemáticas.

## 4. DICIONÁRIO DE DADOS DO SISTEMA (02_dicionario.md)
Mapeamento unificado contendo as definições de tipagem nativa para o SQLite:
- **Entidade tecnico_solicitante:** Campos `id_tecnico` (INTEGER, PK), `nome_metrologista` (VARCHAR), e `matricula` (VARCHAR).
- **Entidade equipamento:** Campos `id_equipamento` (INTEGER, PK), `codigo_tag` (VARCHAR, UNIQUE), `denominacao` (VARCHAR), `fabricante` (VARCHAR), e `data_proxima_calibracao` (DATE).
- **Entidade medicao:** Campos `id_medicao` (INTEGER, PK), `id_tecnico` (INTEGER, FK), `id_equipamento` (INTEGER, FK), `measurement_plan` (VARCHAR), `part_number` (VARCHAR), `nome_caracteristica` (VARCHAR), `valor_nominal` (NUMERIC), `tolerancia_superior` (NUMERIC), `tolerancia_inferior` (NUMERIC), `valor_obtido_media` (NUMERIC) e `status_aprovacao` (VARCHAR).

## 5. SCRIPT DDL DE CRIAÇÃO DAS TABELAS (03_banco.sql)

```sql
PRAGMA foreign_keys = ON;

-- 1. TÉCNICO / SOLICITANTE
CREATE TABLE tecnico_solicitante (
 id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
 nome_metrologista TEXT NOT NULL,
 matricula TEXT NOT NULL
);

-- 2. EQUIPAMENTO
CREATE TABLE equipamento (
 id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
 codigo_tag TEXT UNIQUE NOT NULL,
 denominacao TEXT,
 fabricante TEXT,
 numero_serie TEXT,
 numero_certificado_externo TEXT,
 data_ultima_calibracao DATE,
 data_proxima_calibracao DATE
);

-- 3. MEDIÇÃO
CREATE TABLE medicao (
 id_medicao INTEGER PRIMARY KEY AUTOINCREMENT,
 id_tecnico INTEGER NOT NULL,
 id_equipamento INTEGER NOT NULL,
 
 measurement_plan TEXT NOT NULL, 
 part_number TEXT NOT NULL, 
 nome_caracteristica TEXT NOT NULL,
 
 data_medicao DATE NOT NULL,
 hora_medicao TEXT NOT NULL,
 valor_nominal REAL,
 tolerancia_superior REAL, 
 tolerancia_inferior REAL, 
 medicao_1 REAL,
 medicao_2 REAL,
 media_calculada REAL,
 status_aprovacao TEXT, 
 FOREIGN KEY (id_tecnico)
 REFERENCES tecnico_solicitante(id_tecnico)
 ON DELETE RESTRICT ON UPDATE CASCADE,
 FOREIGN KEY (id_equipamento)
 REFERENCES equipamento(id_equipamento)
 ON DELETE RESTRICT ON UPDATE CASCADE
);
```