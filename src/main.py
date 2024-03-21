from lib.extractor import BrandExtractor, ExtractionResult, extract_brands
from lib.exporter import Exporter
import asyncio

def export_batch(results: list[ExtractionResult]):
    with Exporter() as e:
        for result in results:
            # Itera sobre os resultados de cada extração e exporta cada um para suas
            # respectivas tabelas
            e.export_data('brands', result['brand'])
            e.export_data('models', result['models'])
            e.export_data('years', result['years'])
            e.export_data('fipe', result['data'])

async def execute_pipeline(chunk_size=20, limit=-1):
    """
    chunk_size: Define a quantidade de dados a serem extraídos concorrentemente
    limit: Define o limite de quantidade de dados a ser extraída para cada marca 
    """

    # Cria as instâncias de extratores para cada marca extraída da API
    extractors = [BrandExtractor(b, limit) for b in extract_brands()]

    # Cria as tasks de extração dos dados para serem executadas concorrentemente
    # e separa elas em chunks menores para reduzir a carga na API
    tasks = [extractor.stream() for extractor in extractors]
    chunked_tasks = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

    # Aguarda a execução concorrente de cada chunk de tasks e exporta o resultado 
    for chunk in chunked_tasks:
        results = await asyncio.gather(*chunk)
        export_batch(results)

if __name__ == '__main__':
    asyncio.run(execute_pipeline(limit=10))


