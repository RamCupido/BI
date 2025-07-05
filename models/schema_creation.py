def create_schema(cursor, conn):
    
    # Crear tablas si no existen (solo la primera vez)
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
            ESTADO_CIVIL VARCHAR(50),
            NIVEL_INSTRUCCION VARCHAR(100),
            ANALFABETO VARCHAR(5),
            CONSTRAINT UQ_PERSONA UNIQUE(SEXO, EDAD, ESTADO_CIVIL, NIVEL_INSTRUCCION, ANALFABETO)
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hechos_enemdu')
    BEGIN
        CREATE TABLE hechos_enemdu (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            ID_TIEMPO INT,
            ID_UBICACION INT,
            ID_PERSONA INT,
            INGRESO_LABORAL FLOAT,
            INGRESO_PENSION FLOAT,
            POBREZA VARCHAR(2),
            EXTREMA_POBREZA VARCHAR(2),
            EMPLEO VARCHAR(2),
            FEXP FLOAT,
            FOREIGN KEY (ID_TIEMPO) REFERENCES dim_tiempo(ID_TIEMPO),
            FOREIGN KEY (ID_UBICACION) REFERENCES dim_ubicacion(ID_UBICACION),
            FOREIGN KEY (ID_PERSONA) REFERENCES dim_persona(ID_PERSONA)
        )
    END
    """)
    conn.commit()
