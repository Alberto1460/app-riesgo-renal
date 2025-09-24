import boto3
import pandas as pd
from io import StringIO
from datetime import datetime
from botocore.exceptions import ClientError

BUCKET_NAME = 'renal-registros-prod'
CSV_FILENAME = 'registros_prueba_renal.csv'
REGION_NAME = 'us-east-1'

s3 = boto3.client('s3', region_name=REGION_NAME)

def guardar_en_s3(registro: dict):
    try:
        #1.  Intentar leer el archivo CSV existente desde S3
        try:
            # Lee el archivo CSV existente desde S3
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILENAME)
            # Si el archivo existe, cargarlo en un DataFrame mediante obj['Body'] que es un archivo crudo
            df_existente = pd.read_csv(obj['Body'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                # Si el archivo no existe, crear un DataFrame vacío
                df_existente = pd.DataFrame()
            else:
                raise 

        # 2. Crear un nuevo registro como DataFrame
        df_nuevo = pd.DataFrame([registro])
        df_actualizado = pd.concat([df_existente, df_nuevo], ignore_index=True)

        # 3. Convertir CSV en memoria para subir a s3
        csv_buffer = StringIO()
        df_actualizado.to_csv(csv_buffer, index=False)

        # 4. Subir el CSV al bucket de S3
        s3.put_object(Bucket=BUCKET_NAME, Key=CSV_FILENAME, Body=csv_buffer.getvalue())

        print("✅ Datos guardados en S3 correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar en S3: {e}")

def obtener_csv_desde_s3():
    try:
        # Lee si existe un archivo en S3
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILENAME)
        # Si el archivo existe lo lee mediante Body para exportarlo como CSV
        df = pd.read_csv(obj['Body'])
        return df
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print('❌ El servicio S3 no tiene registro alguno')
            return  pd.DataFrame()
        else:
            raise
        
