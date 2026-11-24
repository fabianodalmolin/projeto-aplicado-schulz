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
