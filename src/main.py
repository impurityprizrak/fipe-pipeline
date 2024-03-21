from lib.extractor import BrandExtractor, ExtractionResult, extract_brands
from lib.exporter import Exporter
import asyncio

def export_batch(results: list[ExtractionResult]):
    with Exporter() as e:
        for result in results:
            e.export_data('brands', result['brand'])
            e.export_data('models', result['models'])
            e.export_data('years', result['years'])
            e.export_data('fipe', result['data'])

async def execute_pipeline(chunk_size=20, limit=-1):
    """
    chunk_size: Define a quantidade de dados a serem extraídos concorrentemente
    limit: Define o limite de quantidade de dados a ser extraída para cada marca 
    """

    extractors = [BrandExtractor(b, limit) for b in extract_brands()]
    tasks = [extractor.stream() for extractor in extractors]
    chunked_tasks = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

    for chunk in chunked_tasks:
        results = await asyncio.gather(*chunk)
        export_batch(results)

if __name__ == '__main__':
    asyncio.run(execute_pipeline(limit=10))


