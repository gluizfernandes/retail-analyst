-- Retail Analyst — Malu Doces
-- Schema de sell-out para análise de mercado de chocolates

CREATE TABLE IF NOT EXISTS marcas (
    marca_id   VARCHAR(12)  PRIMARY KEY,
    fabricante VARCHAR(100) NOT NULL,
    nome       VARCHAR(100) NOT NULL,
    segmento   VARCHAR(20)  CHECK (segmento IN ('premium', 'masstige', 'popular')),
    share_pct  DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS skus (
    sku_id       VARCHAR(12)   PRIMARY KEY,
    marca_id     VARCHAR(12)   NOT NULL REFERENCES marcas(marca_id),
    nome_produto VARCHAR(150)  NOT NULL,
    categoria    VARCHAR(30)   CHECK (categoria IN ('tablete','bombom','trufas','drageados','kit_presente','paes_de_mel')),
    peso_g       INTEGER,
    preco_tabela DECIMAL(8,2)  NOT NULL CHECK (preco_tabela > 0)
);

CREATE TABLE IF NOT EXISTS lojas (
    loja_id UUID        PRIMARY KEY,
    rede    VARCHAR(60) NOT NULL,
    canal   VARCHAR(20) CHECK (canal IN ('supermercado','farmacia','conveniencia','atacado')),
    cidade  VARCHAR(100),
    estado  CHAR(2),
    regiao  VARCHAR(20) CHECK (regiao IN ('Sul','Sudeste','Centro-Oeste','Norte','Nordeste'))
);

CREATE TABLE IF NOT EXISTS vendas (
    venda_id         UUID         PRIMARY KEY,
    sku_id           VARCHAR(12)  NOT NULL REFERENCES skus(sku_id),
    loja_id          UUID         NOT NULL REFERENCES lojas(loja_id),
    periodo          VARCHAR(10)  NOT NULL,
    unidades_vendidas INTEGER     CHECK (unidades_vendidas >= 0),
    faturamento_bruto DECIMAL(12,2) CHECK (faturamento_bruto >= 0),
    preco_medio      DECIMAL(8,2) CHECK (preco_medio > 0)
);

CREATE INDEX IF NOT EXISTS idx_vendas_sku_id  ON vendas(sku_id);
CREATE INDEX IF NOT EXISTS idx_vendas_loja_id ON vendas(loja_id);
CREATE INDEX IF NOT EXISTS idx_vendas_periodo ON vendas(periodo);
CREATE INDEX IF NOT EXISTS idx_lojas_estado   ON lojas(estado);
CREATE INDEX IF NOT EXISTS idx_lojas_canal    ON lojas(canal);
CREATE INDEX IF NOT EXISTS idx_skus_marca_id  ON skus(marca_id);

-- ─── Marcas (dados estáticos — 20 marcas reais) ───────────────────────────────

INSERT INTO marcas VALUES
  ('marca-001', 'Mondelēz',  'Lacta',           'popular',   12.40),
  ('marca-002', 'Mondelēz',  'Bis',              'popular',    8.10),
  ('marca-003', 'Mondelēz',  'Sonho de Valsa',   'masstige',   5.30),
  ('marca-004', 'Mondelēz',  'Ouro Branco',      'masstige',   4.20),
  ('marca-005', 'Mondelēz',  'Diamante Negro',   'popular',    3.10),
  ('marca-006', 'Nestlé',    'Kit Kat',          'masstige',   8.20),
  ('marca-007', 'Nestlé',    'Prestígio',        'popular',    6.10),
  ('marca-008', 'Nestlé',    'Alpino',           'masstige',   4.00),
  ('marca-009', 'Nestlé',    'Charge',           'popular',    3.00),
  ('marca-010', 'Nestlé',    'Sensação',         'masstige',   2.50),
  ('marca-011', 'Nestlé',    'Garoto Bombom',    'popular',    4.10),
  ('marca-012', 'Nestlé',    'Serenata de Amor', 'popular',    5.20),
  ('marca-013', 'Nestlé',    'Talento',          'masstige',   3.10),
  ('marca-014', 'Hersheys',  'Hersheys',          'masstige',   4.00),
  ('marca-015', 'Hersheys',  'Special Dark',      'premium',    2.00),
  ('marca-016', 'Ferrero',   'Ferrero Rocher',   'premium',    3.10),
  ('marca-017', 'Ferrero',   'Raffaello',        'premium',    1.20),
  ('marca-018', 'Harald',    'Melken',           'masstige',   2.10),
  ('marca-019', 'Harald',    'Unique',           'premium',    1.80),
  ('marca-020', 'Arcor',     'Bon o Bon',        'popular',    2.60)
ON CONFLICT DO NOTHING;

-- ─── SKUs (dados estáticos — ~50 produtos) ────────────────────────────────────

INSERT INTO skus VALUES
  -- Lacta
  ('sku-001', 'marca-001', 'Lacta Ao Leite 90g',        'tablete',      90,   4.99),
  ('sku-002', 'marca-001', 'Lacta Intense 40% Cacau',   'tablete',     100,   7.99),
  ('sku-003', 'marca-001', 'Lacta Caixa de Bombons',    'bombom',      300,  22.90),
  -- Bis
  ('sku-004', 'marca-002', 'Bis Ao Leite 45g',          'tablete',      45,   3.49),
  ('sku-005', 'marca-002', 'Bis Branco 45g',            'tablete',      45,   3.49),
  ('sku-006', 'marca-002', 'Bis Xtra 45g',              'tablete',      45,   3.99),
  ('sku-007', 'marca-002', 'Bis Leve 24 Pague 20',      'kit_presente', 504,  39.90),
  -- Sonho de Valsa
  ('sku-008', 'marca-003', 'Sonho de Valsa 38g',        'bombom',       38,   2.99),
  ('sku-009', 'marca-003', 'Sonho de Valsa Caixa 120g', 'bombom',      120,  12.90),
  -- Ouro Branco
  ('sku-010', 'marca-004', 'Ouro Branco 15g',           'bombom',       15,   1.99),
  ('sku-011', 'marca-004', 'Ouro Branco Caixa 250g',    'bombom',      250,  24.90),
  -- Diamante Negro
  ('sku-012', 'marca-005', 'Diamante Negro 80g',        'tablete',      80,   4.49),
  -- Kit Kat
  ('sku-013', 'marca-006', 'Kit Kat 45g',               'tablete',      45,   4.99),
  ('sku-014', 'marca-006', 'Kit Kat Dark 45g',          'tablete',      45,   5.49),
  ('sku-015', 'marca-006', 'Kit Kat Chunky 40g',        'tablete',      40,   4.49),
  ('sku-016', 'marca-006', 'Kit Kat Mini Bag 187g',     'drageados',   187,  24.90),
  -- Prestígio
  ('sku-017', 'marca-007', 'Prestígio 33g',             'bombom',       33,   2.49),
  ('sku-018', 'marca-007', 'Prestígio Caixa 180g',      'bombom',      180,  14.90),
  -- Alpino
  ('sku-019', 'marca-008', 'Alpino 25g',                'tablete',      25,   2.99),
  ('sku-020', 'marca-008', 'Alpino Ice 55g',            'tablete',      55,   5.49),
  -- Charge
  ('sku-021', 'marca-009', 'Charge 30g',                'bombom',       30,   2.29),
  -- Sensação
  ('sku-022', 'marca-010', 'Sensação Morango 140g',     'tablete',     140,   7.99),
  -- Garoto Bombom
  ('sku-023', 'marca-011', 'Garoto Caixa Sortida 300g', 'bombom',      300,  19.90),
  ('sku-024', 'marca-011', 'Garoto Caixa Sortida 150g', 'bombom',      150,  11.90),
  -- Serenata de Amor
  ('sku-025', 'marca-012', 'Serenata de Amor 30g',      'bombom',       30,   2.49),
  ('sku-026', 'marca-012', 'Serenata de Amor Cx 200g',  'bombom',      200,  15.90),
  -- Talento
  ('sku-027', 'marca-013', 'Talento Avelã 85g',         'tablete',      85,   6.99),
  ('sku-028', 'marca-013', 'Talento Amendoim 85g',      'tablete',      85,   6.49),
  -- Hershey's
  ('sku-029', 'marca-014', 'Hersheys Ao Leite 82g',    'tablete',      82,   6.49),
  ('sku-030', 'marca-014', 'Hersheys Cookies 82g',     'tablete',      82,   6.99),
  ('sku-031', 'marca-014', 'Hersheys Extra Cremoso',   'tablete',      82,   6.99),
  -- Special Dark
  ('sku-032', 'marca-015', 'Special Dark 70% Cacau',    'tablete',      82,   8.99),
  ('sku-033', 'marca-015', 'Special Dark Nuts 85g',     'tablete',      85,   9.49),
  -- Ferrero Rocher
  ('sku-034', 'marca-016', 'Ferrero Rocher 3un',        'trufas',       37,   8.99),
  ('sku-035', 'marca-016', 'Ferrero Rocher 8un',        'kit_presente', 100,  24.90),
  ('sku-036', 'marca-016', 'Ferrero Rocher 16un',       'kit_presente', 200,  49.90),
  -- Raffaello
  ('sku-037', 'marca-017', 'Raffaello 8un',             'trufas',       80,  22.90),
  -- Melken
  ('sku-038', 'marca-018', 'Melken Ao Leite 1kg',       'tablete',    1000,  39.90),
  ('sku-039', 'marca-018', 'Melken Meio Amargo 1kg',    'tablete',    1000,  41.90),
  -- Unique
  ('sku-040', 'marca-019', 'Unique 75% Cacau 80g',      'tablete',      80,  18.90),
  ('sku-041', 'marca-019', 'Unique Frutas 80g',         'tablete',      80,  19.90),
  -- Bon o Bon
  ('sku-042', 'marca-020', 'Bon o Bon Original 30g',    'bombom',       30,   2.29),
  ('sku-043', 'marca-020', 'Bon o Bon White 30g',       'bombom',       30,   2.49),
  ('sku-044', 'marca-020', 'Bon o Bon Caixa 225g',      'bombom',      225,  13.90)
ON CONFLICT DO NOTHING;
