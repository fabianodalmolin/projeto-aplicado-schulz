# Organização dos Dados - Sistema de Calibração Schulz S.A.

## 1. Divisão do Banco de Dados em Entidades Principais
Para garantir a transição eficiente das planilhas manuais para o novo ambiente estruturado, a modelagem foi dividida estritamente nas 3 entidades principais requisitadas:

*   **Técnico / Solicitante (Metrologista):** Armazena as informações de identificação dos operadores e revisores responsáveis pelos ensaios (ex: matrícula/RE, nome do metrologista).
*   **Equipamento:** Centraliza os dados estáticos dos instrumentos de medição e dos padrões de referência do laboratório (ex: código TAG do ativo, denominação, fabricante, número de série e data de vigência da calibração).
*   **Medição:** Registra o cabeçalho e o corpo dos ensaios de calibração gerados a partir do software Zeiss Calypso. Esta entidade vincula dinamicamente qual Técnico operou qual Equipamento, guardando os resultados dimensionais (plano de medição, características geométricas, valores nominais, limites de tolerância e status de aprovação).

## 2. Importância de Evitar Dados Duplicados (Normalização)
A eliminação da redundância de dados através da separação nessas três entidades traz impactos diretos na operação da Schulz S.A.:

*   **Integridade e Consistência:** Em planilhas manuais, erros de digitação ao repetir o nome de um metrologista ou fabricante quebram a rastreabilidade exigida por auditorias (ISO 9001). Com tabelas normalizadas, cada entidade possui um registro único. Se um setor de cliente interno mudar, a atualização ocorre em um só lugar.
*   **Otimização de Armazenamento:** Em vez de repetir strings textuais longas como "Máquina de medição por coordenadas Carl Zeiss" em cada uma das milhares de linhas de características medidas, armazena-se apenas o ID numérico de referência, economizando espaço em disco e acelerando as consultas do sistema.
*   **Confiabilidade em Auditorias Externas:** Isolar a medição do cadastro do instrumento garante que o histórico cronológico de calibrações seja mantido intacto. Isso elimina falhas históricas do Excel da fábrica, como os erros críticos de macro ou células com #DIV/0! e #VALOR!, preservando a imutabilidade das regras metrológicas no backend.
