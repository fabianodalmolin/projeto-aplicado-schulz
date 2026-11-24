import sqlite3

MARGEM_FLOAT = 1e-7
NOME_BANCO = "metrologia_schulz.db"

class Tecnico:
    def __init__(self, nome, matricula, id_tecnico=None):
        self._id_tecnico = id_tecnico
        self.nome = nome
        self.matricula = matricula

    @property
    def id_tecnico(self):
        return self._id_tecnico

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        valor = str(valor).strip()
        if not valor:
            raise ValueError("O nome do técnico é obrigatório.")
        self._nome = valor

    @property
    def matricula(self):
        return self._matricula

    @matricula.setter
    def matricula(self, valor):
        valor = str(valor).strip().upper()
        if not valor:
            raise ValueError("A matrícula é obrigatória.")
        self._matricula = valor


class Equipamento:
    def __init__(self, codigo_tag, denominacao, fabricante="Schulz", 
                 numero_serie="S/N", numero_certificado_externo="N/A", 
                 data_ultima_calibracao="2026-01-01", 
                 data_proxima_calibracao="2027-01-01", id_equipamento=None):
        self._id_equipamento = id_equipamento
        self.codigo_tag = codigo_tag
        self.denominacao = denominacao
        self.fabricante = fabricante
        self.numero_serie = numero_serie
        self.numero_certificado_externo = numero_certificado_externo
        self.data_ultima_calibracao = data_ultima_calibracao
        self.data_proxima_calibracao = data_proxima_calibracao

    @property
    def id_equipamento(self):
        return self._id_equipamento

    @property
    def codigo_tag(self):
        return self._codigo_tag

    @codigo_tag.setter
    def codigo_tag(self, valor):
        valor = str(valor).strip().upper()
        if not valor:
            raise ValueError("A TAG do equipamento é obrigatória.")
        self._codigo_tag = valor

    @property
    def denominacao(self):
        return self._denominacao

    @denominacao.setter
    def denominacao(self, valor):
        valor = str(valor).strip()
        self._denominacao = valor if valor else "Não Especificado"


class Medicao:
    def __init__(self, id_tecnico, id_equipamento, measurement_plan, part_number, 
                 nome_caracteristica, data_medicao, hora_medicao, valor_nominal, 
                 tolerancia_superior, tolerancia_inferior, medicao_1, medicao_2, 
                 id_medicao=None):
        self._id_medicao = id_medicao
        self.id_tecnico = id_tecnico
        self.id_equipamento = id_equipamento
        self.measurement_plan = str(measurement_plan).strip().upper()
        self.part_number = str(part_number).strip().upper()
        self.nome_caracteristica = str(nome_caracteristica).strip()
        self.data_medicao = str(data_medicao).strip()
        self.hora_medicao = str(hora_medicao).strip()

        self._valor_nominal = self._para_numero(valor_nominal, "Valor Nominal")
        self._tolerancia_superior = self._para_numero(tolerancia_superior, "Tolerância Superior")
        self._tolerancia_inferior = self._para_numero(tolerancia_inferior, "Tolerância Inferior")
        self._medicao_1 = self._para_numero(medicao_1, "Medição 1")
        self._medicao_2 = self._para_numero(medicao_2, "Medição 2")

        if self._tolerancia_inferior > self._tolerancia_superior:
            raise ValueError("A tolerância inferior não pode ser maior que a superior.")

    @staticmethod
    def _para_numero(valor, nome_campo):
        try:
            texto = str(valor).strip().replace(",", ".")
            return float(texto)
        except ValueError:
            raise ValueError(f"O campo '{nome_campo}' precisa ser numérico (recebido: '{valor}').")

    @property
    def id_medicao(self):
        return self._id_medicao

    @property
    def media_calculada(self):
        return round((self._medicao_1 + self._medicao_2) / 2, 4)

    def esta_aprovada(self):
        media = self.media_calculada
        return (self._tolerancia_inferior - MARGEM_FLOAT) <= media <= (self._tolerancia_superior + MARGEM_FLOAT)

    @property
    def status_aprovacao(self):
        return "APROVADO" if self.esta_aprovada() else "REPROVADO"
class DatabaseManager:
    def __init__(self, db_name=NOME_BANCO):
        self.db_name = db_name

    def conectar(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def inicializar_banco(self):
        with self.conectar() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS tecnico_solicitante (
                id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_metrologista TEXT NOT NULL,
                matricula TEXT NOT NULL UNIQUE
            );
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


class TecnicoDAO:
    def __init__(self, db):
        self.db = db

    def inserir(self, tecnico):
        sql = "INSERT INTO tecnico_solicitante (nome_metrologista, matricula) VALUES (?, ?)"
        try:
            with self.db.conectar() as conn:
                cursor = conn.execute(sql, (tecnico.nome, tecnico.matricula))
                tecnico._id_tecnico = cursor.lastrowid
                return tecnico
        except sqlite3.IntegrityError:
            return self.buscar_por_matricula(tecnico.matricula)

    def buscar_por_matricula(self, matricula):
        matricula = str(matricula).strip().upper()
        with self.db.conectar() as conn:
            linha = conn.execute("SELECT * FROM tecnico_solicitante WHERE matricula = ?", (matricula,)).fetchone()
            if linha:
                return Tecnico(linha["nome_metrologista"], linha["matricula"], id_tecnico=linha["id_tecnico"])
            return None


class EquipamentoDAO:
    def __init__(self, db):
        self.db = db

    def inserir(self, eq):
        sql = """INSERT INTO equipamento (codigo_tag, denominacao, fabricante, numero_serie, 
                 numero_certificado_externo, data_ultima_calibracao, data_proxima_calibracao) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db.conectar() as conn:
                cursor = conn.execute(sql, (eq.codigo_tag, eq.denominacao, eq.fabricante, eq.numero_serie,
                                            eq.numero_certificado_externo, eq.data_ultima_calibracao, eq.data_proxima_calibracao))
                eq._id_equipamento = cursor.lastrowid
                return eq
        except sqlite3.IntegrityError:
            return self.buscar_por_tag(eq.codigo_tag)

    def buscar_por_tag(self, codigo_tag):
        codigo_tag = str(codigo_tag).strip().upper()
        with self.db.conectar() as conn:
            linha = conn.execute("SELECT * FROM equipamento WHERE codigo_tag = ?", (codigo_tag,)).fetchone()
            if linha:
                return Equipamento(linha["codigo_tag"], linha["denominacao"], linha["fabricante"],
                                   linha["numero_serie"], linha["numero_certificado_externo"],
                                   linha["data_ultima_calibracao"], linha["data_proxima_calibracao"],
                                   id_equipamento=linha["id_equipamento"])
            return None

    def atualizar_denominacao(self, codigo_tag, nova_denominacao):
        codigo_tag = str(codigo_tag).strip().upper()
        with self.db.conectar() as conn:
            cursor = conn.execute("UPDATE equipamento SET denominacao = ? WHERE codigo_tag = ?", 
                                  (nova_denominacao.strip(), codigo_tag))
            return cursor.rowcount == 1


class MedicaoDAO:
    def __init__(self, db):
        self.db = db

    def inserir(self, med):
        sql = """INSERT INTO medicao (id_tecnico, id_equipamento, measurement_plan, part_number, 
                 nome_caracteristica, data_medicao, hora_medicao, valor_nominal, 
                 tolerancia_superior, tolerancia_inferior, medicao_1, medicao_2, 
                 media_calculada, status_aprovacao) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db.conectar() as conn:
                cursor = conn.execute(sql, (med.id_tecnico, med.id_equipamento, med.measurement_plan, med.part_number,
                                            med.nome_caracteristica, med.data_medicao, med.hora_medicao, med._valor_nominal,
                                            med._tolerancia_superior, med._tolerancia_inferior, med._medicao_1, med._medicao_2,
                                            med.media_calculada, med.status_aprovacao))
                med._id_medicao = cursor.lastrowid
                return med
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Erro de vínculo no banco (Técnico ou Equipamento inválido): {e}")

    def relatorio_por_tag(self, codigo_tag):
        codigo_tag = str(codigo_tag).strip().upper()
        sql = """
            SELECT m.id_medicao, t.nome_metrologista, t.matricula, e.codigo_tag, e.denominacao,
                   m.part_number, m.nome_caracteristica, m.valor_nominal, m.tolerancia_inferior,
                   m.tolerancia_superior, m.media_calculada, m.status_aprovacao, m.data_medicao
            FROM medicao m
            INNER JOIN tecnico_solicitante t ON m.id_tecnico = t.id_tecnico
            INNER JOIN equipamento e ON m.id_equipamento = e.id_equipamento
            WHERE e.codigo_tag = ?
            ORDER BY m.id_medicao
        """
        with self.db.conectar() as conn:
            return conn.execute(sql, (codigo_tag,)).fetchall()
