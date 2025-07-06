def create_vivienda_schema(cursor, conn):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_tipo_vivienda')
    BEGIN
        CREATE TABLE dim_tipo_vivienda (
            ID_TIPO_VIVIENDA INT IDENTITY(1,1) PRIMARY KEY,
            DESCRIPCION VARCHAR(100) UNIQUE
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_material_vivienda')
    BEGIN
        CREATE TABLE dim_material_vivienda (
            ID_MATERIAL INT IDENTITY(1,1) PRIMARY KEY,
            MATERIAL_TECHO VARCHAR(100),
            MATERIAL_PARED VARCHAR(100),
            MATERIAL_PISO VARCHAR(100),
            CONSTRAINT UQ_MATERIAL UNIQUE(MATERIAL_TECHO, MATERIAL_PARED, MATERIAL_PISO)
        )
    END

    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hechos_vivienda')
    BEGIN
        CREATE TABLE hechos_vivienda (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            ID_TIEMPO INT,
            ID_UBICACION INT,
            ID_TIPO_VIVIENDA INT,
            ID_MATERIAL INT,
            ACCESO_AGUA VARCHAR(2),
            ACCESO_ELECTRICIDAD VARCHAR(2),
            FOREIGN KEY (ID_TIEMPO) REFERENCES dim_tiempo(ID_TIEMPO),
            FOREIGN KEY (ID_UBICACION) REFERENCES dim_ubicacion(ID_UBICACION),
            FOREIGN KEY (ID_TIPO_VIVIENDA) REFERENCES dim_tipo_vivienda(ID_TIPO_VIVIENDA),
            FOREIGN KEY (ID_MATERIAL) REFERENCES dim_material_vivienda(ID_MATERIAL)
        )
    END
    """)
    conn.commit()
    print("Esquema de base de datos de vivienda creado o verificado correctamente")