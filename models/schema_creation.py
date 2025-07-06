def create_schema_persona(cursor, conn):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_tiempo')
    BEGIN
        CREATE TABLE dim_tiempo (
            ID_TIEMPO INT IDENTITY(1,1) PRIMARY KEY,
            PERIODO VARCHAR(10) UNIQUE
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_ubicacion')
    BEGIN
        CREATE TABLE dim_ubicacion (
            ID_UBICACION INT IDENTITY(1,1) PRIMARY KEY,
            PROVINCIA VARCHAR(100),
            REGION VARCHAR(50),
            CONSTRAINT UQ_PROVINCIA_REGION UNIQUE(PROVINCIA, REGION)
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_persona')
    BEGIN
        CREATE TABLE dim_persona (
            ID_PERSONA INT IDENTITY(1,1) PRIMARY KEY,
            SEXO VARCHAR(10),
            EDAD INT,
            ANALFABETO VARCHAR(5),
            CONSTRAINT UQ_PERSONA UNIQUE(SEXO, EDAD, ANALFABETO)
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_educacion')
    BEGIN
        CREATE TABLE dim_educacion (
            ID_EDUCACION INT IDENTITY(1,1) PRIMARY KEY,
            NIVEL_INSTRUCCION VARCHAR(100) UNIQUE
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_estado_civil')
    BEGIN
        CREATE TABLE dim_estado_civil (
            ID_ESTADO_CIVIL INT IDENTITY(1,1) PRIMARY KEY,
            ESTADO_CIVIL VARCHAR(50) UNIQUE
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hechos_enemdu')
    BEGIN
        CREATE TABLE hechos_enemdu (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            ID_TIEMPO INT,
            ID_UBICACION INT,
            ID_PERSONA INT,
            ID_EDUCACION INT,
            ID_ESTADO_CIVIL INT,
            INGRESO_LABORAL FLOAT,
            INGRESO_PENSION FLOAT,
            POBREZA VARCHAR(2),
            EXTREMA_POBREZA VARCHAR(2),
            EMPLEO VARCHAR(2),
            FEXP FLOAT,
            FOREIGN KEY (ID_TIEMPO) REFERENCES dim_tiempo(ID_TIEMPO),
            FOREIGN KEY (ID_UBICACION) REFERENCES dim_ubicacion(ID_UBICACION),
            FOREIGN KEY (ID_PERSONA) REFERENCES dim_persona(ID_PERSONA),
            FOREIGN KEY (ID_EDUCACION) REFERENCES dim_educacion(ID_EDUCACION),
            FOREIGN KEY (ID_ESTADO_CIVIL) REFERENCES dim_estado_civil(ID_ESTADO_CIVIL)
        )
    END
    """)
    conn.commit()
    
    print("Esquema de base de datos de persona creado o verificado correctamente.")