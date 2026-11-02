import sqlite3
import os

class DatabaseManager:
    
    def __init__(self, db_name="metrologia_schulz.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def conectar(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            return self.conn
        except sqlite3.Error as e:
            print(f"❌ Erro ao conectar ao banco de dados: {e}")
            return None

    def desconectar(self):
        if self.conn:
            self.conn.close()

    def inicializar_banco(self):
        self.conectar()
        
        try:
            # 1. TABELA TÉCNICO / SOLICITANTE
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tecnico_solicitante (
                id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_metrologista TEXT NOT NULL,
                matricula TEXT NOT NULL
            );
            """)

            # 2. TABELA EQUIPAMENTO
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipamento (
                id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_tag TEXT UNIQUE NOT NULL,
                denominacao TEXT,
                fabricante TEXT,
                numero_serie TEXT,
                numero_certificado_externo TEXT,
                data_ultima_calibracao DATE,
                data_proxima_calibracao DATE
            );
            """)

            # 3. TABELA MEDIÇÃO
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicao (
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
                FOREIGN KEY (id_tecnico) REFERENCES tecnico_solicitante(id_tecnico) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (id_equipamento) REFERENCES equipamento(id_equipamento) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """)
            
            self.conn.commit()
            print("💾 Banco de dados e tabelas validados/criados com sucesso!")
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao estruturar tabelas: {e}")
        finally:
            self.desconectar()

# Teste de execução do Dia 1
if __name__ == "__main__":
    db = DatabaseManager()
    db.inicializar_banco()
class Tecnico:
    # Representa a entidade do metrologista/ calibrador
    def __init__(self, nome, matricula, id_tecnico=None):
        self.id_tecnico = id_tecnico
        self.nome = nome
        self.matricula = matricula

    def salvar(self, db_manager):
        # Insere o técnico no banco de dados SQLite.
        db_manager.conectar()
        try:
            db_manager.cursor.execute("""
                INSERT INTO tecnico_solicitante (nome_metrologista, matricula)
                VALUES (?, ?);
            """, (self.nome, self.matricula))
            db_manager.conn.commit()
            self.id_tecnico = db_manager.cursor.lastrowid
            print(f"👤 Técnico {self.nome} cadastrado com ID {self.id_tecnico}!")
        except sqlite3.Error as e:
            print(f"❌ Erro ao salvar técnico: {e}")
        finally:
            db_manager.desconectar()


class Equipamento:
    # equipamentos de medição e MMC
    def __init__(self, codigo_tag, denominacao, fabricante, numero_serie, 
                 numero_certificado_externo, data_ultima_calibracao, 
                 data_proxima_calibracao, id_equipamento=None):
        self.id_equipamento = id_equipamento
        self.codigo_tag = codigo_tag
        self.denominacao = denominacao
        self.fabricante = fabricante
        self.numero_serie = numero_serie
        self.numero_certificado_externo = numero_certificado_externo
        self.data_ultima_calibracao = data_ultima_calibracao
        self.data_proxima_calibracao = data_proxima_calibracao

    def salvar(self, db_manager):
        # Insere o equipamento no banco de dados
        db_manager.conectar()
        try:
            db_manager.cursor.execute("""
                INSERT INTO equipamento (codigo_tag, denominacao, fabricante, numero_serie, 
                                         numero_certificado_externo, data_ultima_calibracao, data_proxima_calibracao)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (self.codigo_tag, self.denominacao, self.fabricante, self.numero_serie,
                  self.numero_certificado_externo, self.data_ultima_calibracao, self.data_proxima_calibracao))
            db_manager.conn.commit()
            self.id_equipamento = db_manager.cursor.lastrowid
            print(f"⚙️ Equipamento TAG {self.codigo_tag} cadastrado com ID {self.id_equipamento}!")
        except sqlite3.Error as e:
            print(f"❌ Erro ao salvar equipamento (verifique se a TAG é única): {e}")
        finally:
            db_manager.desconectar()


class Medicao:
    # Encapsulamento do ensaio de calibração e validação das regras metrológicas
    def __init__(self, id_tecnico, id_equipamento, measurement_plan, part_number, 
                 nome_caracteristica, data_medicao, hora_medicao, valor_nominal, 
                 tolerancia_superior, tolerancia_inferior, medicao_1, medicao_2, id_medicao=None):
        self.id_medicao = id_medicao
        self.id_tecnico = id_tecnico
        self.id_equipamento = id_equipamento
        self.measurement_plan = measurement_plan
        self.part_number = part_number
        self.nome_caracteristica = nome_caracteristica
        self.data_medicao = data_medicao
        self.hora_medicao = hora_medicao
        self.valor_nominal = valor_nominal
        self.tolerancia_superior = tolerancia_superior
        self.tolerancia_inferior = tolerancia_inferior
        self.medicao_1 = medicao_1
        self.medicao_2 = medicao_2
        
        # Atributos calculados automaticamente por regras de negócio
        self.media_calculada = None
        self.status_aprovacao = None
        self.processar_regras_metrologicas()

    def processar_regras_metrologicas(self):
        # Calcula a média física e define o status de aprovação baseado nas tolerâncias.
        # 1. Calcula a média aritmética das duas passagens da máquina
        self.media_calculada = round((self.medicao_1 + self.medicao_2) / 2, 4)
        
        # 2. Valida contra os limites de engenharia da Schulz
        if self.tolerancia_inferior <= self.media_calculada <= self.tolerancia_superior:
            self.status_aprovacao = "APROVADO"
        else:
            self.status_aprovacao = "REPROVADO"

    def salvar(self, db_manager):
        # Insere a medição processada no banco de dados SQLite.
        db_manager.conectar()
        try:
            db_manager.cursor.execute("""
                INSERT INTO medicao (id_tecnico, id_equipamento, measurement_plan, part_number, 
                                     nome_caracteristica, data_medicao, hora_medicao, valor_nominal, 
                                     tolerancia_superior, tolerancia_inferior, medicao_1, medicao_2, 
                                     media_calculada, status_aprovacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (self.id_tecnico, self.id_equipamento, self.measurement_plan, self.part_number,
                  self.nome_caracteristica, self.data_medicao, self.hora_medicao, self.valor_nominal,
                  self.tolerancia_superior, self.tolerancia_inferior, self.medicao_1, self.medicao_2,
                  self.media_calculada, self.status_aprovacao))
            db_manager.conn.commit()
            self.id_medicao = db_manager.cursor.lastrowid
            print(f"📊 Medição {self.nome_caracteristica} salva! Status: {self.status_aprovacao}")
        except sqlite3.Error as e:
            print(f"❌ Erro ao salvar medição: {e}")
        finally:
            db_manager.desconectar()
