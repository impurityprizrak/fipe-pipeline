from lib.extractor import BrandExtractor, extract_brands
from lib.exporter import Exporter
from lib.utils import unify_results
import asyncio

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
        unified = unify_results(results)

        with Exporter(unified) as e:
            e.export_data()
        
if __name__ == '__main__':
    asyncio.run(execute_pipeline(limit=10))


