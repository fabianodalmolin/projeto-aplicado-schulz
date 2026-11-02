import sqlite3
import os
from classes_04 import DatabaseManager, Tecnico, Equipamento, Medicao

# Bloco criado apenas para testar a aplicação, pois Apaga o banco de dados antigo antes de iniciar a simulação para evitar erros de duplicidade
if os.path.exists("metrologia_schulz.db"):
    try:
        os.remove("metrologia_schulz.db")
    except PermissionError:
        pass

def emitir_relatorio_terminal(db_manager):
    """Executa uma consulta relacional com JOIN e exibe o relatório no terminal."""
    db_manager.conectar()
    
    query = """
        SELECT 
            m.id_medicao,
            t.nome_metrologista,
            t.matricula,
            e.codigo_tag,
            e.denominacao,
            m.part_number,
            m.nome_caracteristica,
            m.valor_nominal,
            m.tolerancia_inferior,
            m.tolerancia_superior,
            m.media_calculada,
            m.status_aprovacao,
            m.data_medicao,
            m.hora_medicao
        FROM medicao m
        INNER JOIN tecnico_solicitante t ON m.id_tecnico = t.id_tecnico
        INNER JOIN equipamento e ON m.id_equipamento = e.id_equipamento;
    """
    
    try:
        db_manager.cursor.execute(query)
        registros = db_manager.cursor.fetchall()
        
        print("\n" + "="*80)
        print("         SCHULZ S.A. - SISTEMA INTEGRADO DE REGISTROS METROLÓGICOS        ")
        print("                     RELATÓRIO DE ENSAIOS DE CALIBRAÇÃO                   ")
        print("="*80)
        
        if not registros:
            print("Nenhum registro de medição localizado no banco de dados.")
            return

        for reg in registros:
            print(f"ID Medição: {reg[0]} | Data: {reg[12]} {reg[13]}")
            print(f"Metrologista: {reg[1]} (Matrícula: {reg[2]})")
            print(f"Equipamento / MMC: {reg[4]} (TAG: {reg[3]})")
            print(f"Part Number (Peça): {reg[5]} | Característica: {reg[6]}")
            print("-" * 80)
            print(f"Nominal: {reg[7]} mm  |  Tolerâncias: [{reg[8]} mm a {reg[9]} mm]")
            print(f"Média Física Obtida: {reg[10]} mm")
            
            
            status = reg[11]
            status_formatado = f"🟢 [{status}]" if status == "APROVADO" else f"🔴 [{status}]"
            print(f"STATUS FINAL: {status_formatado}")
            print("="*80)
            
    except sqlite3.Error as e:
        print(f"❌ Erro ao gerar relatório relacional: {e}")
    finally:
        db_manager.desconectar()


def main():
    # 1. Inicializa o gerenciador do banco de dados
    db = DatabaseManager()
    db.inicializar_banco() # Garante as tabelas prontas do Dia 1
    
    print("\n🚀 Iniciando simulação de carga de dados metrológicos...")

    # 2. Instancia e salva um Técnico (Metrologista)
    metrologista = Tecnico(nome="Fabiano Dalmolin", matricula="RE-2026X")
    metrologista.salvar(db)

    # 3. Instancia e salva um Equipamento (Máquina de Medir por Coordenadas)
    mmc_zeiss = Equipamento(
        codigo_tag="MMC-01-ZEISS",
        denominacao="Máquina Tridimensional Calypso",
        fabricante="Zeiss",
        numero_serie="Z-998877",
        numero_certificado_externo="CERT-2026-A",
        data_ultima_calibracao="2026-01-15",
        data_proxima_calibracao="2027-01-15"
    )
    mmc_zeiss.salvar(db)

    # Se os objetos foram salvos e possuem IDs gerados pelo banco, avançamos para as medições
    if metrologista.id_tecnico and mmc_zeiss.id_equipamento:
        
        # 4. Caso de Teste 1: Medição que deve ser APROVADA
        medicao_ok = Medicao(
            id_tecnico=metrologista.id_tecnico,
            id_equipamento=mmc_zeiss.id_equipamento,
            measurement_plan="PLANO_CABECOTE_01",
            part_number="PN-99234-A",
            nome_caracteristica="Diâmetro do Cilindro Interno",
            data_medicao="2026-10-28",
            hora_medicao="14:35:00",
            valor_nominal=50.0000,
            tolerancia_superior=50.0500,
            tolerancia_inferior=49.9500,
            medicao_1=50.0100,
            medicao_2=49.9900
        )
        medicao_ok.salvar(db)

        # 5. Caso de Teste 2: Medição que deve ser REPROVADA
        medicao_falha = Medicao(
            id_tecnico=metrologista.id_tecnico,
            id_equipamento=mmc_zeiss.id_equipamento,
            measurement_plan="PLANO_EIXO_VIRABREQUIM",
            part_number="PN-88412-B",
            nome_caracteristica="Espessura do Ressalto Lateral",
            data_medicao="2026-10-28",
            hora_medicao="14:42:15",
            valor_nominal=12.0000,
            tolerancia_superior=12.1000,
            tolerancia_inferior=11.9000,
            medicao_1=12.1500,
            medicao_2=12.1100
        )
        medicao_falha.salvar(db)

        # 6. Exibição do relatório relacional cruzado com os JOINs
        emitir_relatorio_terminal(db)

if __name__ == "__main__":
    main()
