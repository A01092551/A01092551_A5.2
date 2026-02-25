# pylint: disable=invalid-name
"""
Módulo para calcular el costo total de ventas a partir de un catálogo de
precios y un registro de ventas en formato JSON.

El nombre del archivo no cumple con PEP8 'computeSales', sin embargo
se deja debido a que está en las especificaciones solicitadas.
"""

import sys
import time
import json
import logging
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def read_data_from_file(file_path):
    """
    Lee el archivo JSON proporcionado y devuelve su contenido.
    Retorna None si hay algún error o si el archivo está vacío.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not data:
            logging.error("El archivo '%s' no contiene datos.", file_path)
            return None

        return data

    except FileNotFoundError:
        logging.error("Archivo '%s' no encontrado.", file_path)
        return None
    except (IOError, OSError) as error:
        logging.error("Error al leer archivo '%s': %s", file_path, error)
        return None
    except json.JSONDecodeError as error:
        logging.error(
            "El archivo '%s' no es un JSON válido: %s",
            file_path,
            error
        )

    return None


def calculate_sales(sales, prices):
    """
    Recorre la lista de ventas y suma el precio de cada producto.
    """

    # Convertir lista de precios en diccionario
    price_lookup = {
        item.get("title"): item.get("price", 0)
        for item in prices
        if isinstance(item, dict)
    }

    total = 0.0

    for sale in sales:
        if not isinstance(sale, dict):
            continue

        product_name = sale.get("Product")
        quantity = sale.get("Quantity", 0)

        if product_name in price_lookup:
            total += price_lookup[product_name] * quantity
        else:
            logging.warning(
                "El producto '%s' no está en el catálogo de precios.",
                product_name
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

        file_exists = output_file.exists()
        file_empty = file_exists and output_file.stat().st_size == 0

        with open(output_file, "a", encoding="utf-8") as file:

            if not file_exists or file_empty:
                header = (
                    f"{'Archivo':<20}"
                    f"{'Total':<15}"
                    f"{'Tiempo (segundos)':<20}\n"
                    f"{'-' * 55}\n"
                )
                file.write(header)

            row = (
                f"{sales_file_name_short:<20}"
                f"{sum_of_sales:<15.2f}"
                f"{elapsed_time:<20.4f}\n"
            )
            file.write(row)

        logging.info("Resultados guardados en: %s", output_file)

    except (IOError, OSError) as error:
        logging.error("Error al escribir resultados: %s", error)


def main():
    """
    Función principal para ejecutar el cálculo de ventas.
    """
    if len(sys.argv) < 3:
        logging.error(
            "Uso: python computeSales.py "
            "priceCatalogue.json salesRecord.json"
        )
        sys.exit(1)

    prices_file_name = sys.argv[1]
    sales_file_name = sys.argv[2]

    script_dir = Path(__file__).parent
    prices_file_path = script_dir.parent / "tests" / prices_file_name
    sales_file_path = script_dir.parent / "tests" / sales_file_name

    start_time = time.time()

    logging.info("Leyendo precios de: %s", prices_file_name)
    prices = read_data_from_file(prices_file_path)

    logging.info("Leyendo ventas de: %s", sales_file_name)
    sales = read_data_from_file(sales_file_path)

    if prices is None or sales is None:
        sys.exit(1)

    sum_of_sales = calculate_sales(sales, prices)

    elapsed_time = time.time() - start_time

    logging.info("Total de las ventas: %.2f", sum_of_sales)
    logging.info("Tiempo transcurrido: %.4f segundos", elapsed_time)

    write_results_to_file(sales_file_name, sum_of_sales, elapsed_time)


if __name__ == "__main__":
    main()
