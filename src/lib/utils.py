from .extractor import ExtractionResult

def unify_results(results: list[ExtractionResult]):
    unified = ExtractionResult(brand=[], models=[], years=[], data=[])

    for result in results:
        for key, value in result.items():
            unified[key].extend(value)
    
    return unified