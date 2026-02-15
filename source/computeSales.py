# pylint: disable=invalid-name
"""
Módulo para calcular el costo total de ventas a partir de un catálogo de
precios y un registro de ventas en formato JSON.

El nombre del archivo no cumple con PEP8 'computeSales', sin embargo
se deja debido a que está en las especificaciones solicitadas.
"""

import sys
import time
# Librería para trabajar con archivos json
import json
from pathlib import Path


def read_data_from_file(file_path):
    """
    Lee el archivo json proporcionado, devuelve un diccionario.
    Requiere la ubicación del archivo.
    Maneja errores por ruta incorrecta, problemas al abrir el archivo y datos
    faltantes

    """

    # Este try intenta abrir el archivo, sino puede, muestra error y continúa
    try:
        # Se abre el archivo en modo lectura
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validar que tenga contenido útil
        if not data:
            print(f"Error: El archivo '{file_path}' no contiene datos")
            return []

    except FileNotFoundError:
        print(f"Error: Archivo '{file_path}' no encontrado.")
        return []
    except (IOError, OSError) as error:
        print(f"Error al leer archivo: {error}")
        return []
    except json.JSONDecodeError as error:
        print(f"Error: El archivo '{file_path}' no es un JSON válido: {error}")
        return []

    return data


def calculate_sales(sales, prices):
    """
    Recorre la lista de ventas y suma el precio de cada producto.
    Requiere los diccionarios de precios y ventas.
    """

    total = 0.0

    for sale in sales:
        product_name = sale.get("Product")
        quantity = sale.get("Quantity", 0)

        found = False

        for item in prices:
            if item.get("title") == product_name:
                total += item.get("price", 0) * quantity
                found = True
                break

        if not found:
            print(
                f"\nEste producto: '{product_name}' no está en el "
                f"catálogo de precios"
            )

    return total


def write_results_to_file(sales_file_name, sum_of_sales, elapsed_time):
    """
    Escribe resultados en SalesResults.txt.
    Solo agrega encabezados si el archivo no existe o está vacío.
    """

    sales_file_name_short = sales_file_name.split(".")[0]

    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "results"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "SalesResults.txt"

        # Verificar si el archivo ya existe y si está vacío
        file_exists = output_file.exists()
        file_empty = file_exists and output_file.stat().st_size == 0

        with open(output_file, 'a', encoding='utf-8') as file:

            # Si no existe o está vacío → escribir encabezado
            if not file_exists or file_empty:
                header = (
                    f"{'Archivo':<20}{'Total':<15}{'Tiempo (segundos)':<15}\n"
                    f"{'-'*50}\n"
                )
                file.write(header)

            # Escribir solo los valores
            row = (
                f"{sales_file_name_short:<20}{sum_of_sales:<15.2f}"
                f"{elapsed_time:<15.4f}\n"
            )
            file.write(row)

        print(f"\nResultados guardados en: {output_file}")

    except (IOError, OSError) as error:
        print(f"Error al escribir resultados en archivo: {error}")


def main():
    """
    Función principal para ejecutar el cálculo de ventas.
    """
    # Verifica que se hayan pasado la cantidad de archivos correctos
    if len(sys.argv) < 3:
        print(
            "Uso: python computeSales.py priceCatalogue.json "
            "salesRecord.json"
        )
        sys.exit(1)

    # Guarda los nombres de los archivos
    prices_file_name = sys.argv[1]
    sales_file_name = sys.argv[2]

    # Apunta a una carpeta arriba de la carpeta source
    script_dir = Path(__file__).parent
    # Apunta a la carpeta tests y el nombre del archivo prices
    prices_file_path = script_dir.parent / "tests" / prices_file_name
    # Apunta a la carpeta tests y el nombre del archivo sales
    sales_file_path = script_dir.parent / "tests" / sales_file_name

    # Empieza a contar el tiempo
    start_time = time.time()

    print(f"Leyendo precios de: {prices_file_name}")
    prices = read_data_from_file(prices_file_path)
    print(f"\nLeyendo ventas de: {sales_file_name}")
    sales = read_data_from_file(sales_file_path)

    # Función para sumar las ventas
    sum_of_sales = calculate_sales(sales, prices)

    # Muestra el tiempo transcurrido
    elapsed_time = time.time() - start_time

    print(f"\nEl total de las ventas es: {sum_of_sales:.2f}")
    print(f"\nTiempo transcurrido: {elapsed_time:.4f} segundos\n")

    # Guarda los resultados en un archivo
    write_results_to_file(sales_file_name, sum_of_sales, elapsed_time)


if __name__ == "__main__":
    main()
