import re
import json
import random
import time
import asyncio
import aiohttp
import requests
from .data_types import *
from typing import Any, TypedDict

BASE_URL = 'https://parallelum.com.br/fipe/api/v1/carros'

def extract_brands():
    url = BASE_URL+'/marcas'
    response = requests.get(url)
    data = response.text

    if response.status_code >= 400:
        raise RuntimeError(f"Failed to extract brands from api due to an exception: {data}")
    
    brands: list[dict[str, str]] = json.loads(data)
    
    for brand in brands:
        brand_data = Brand(brand['codigo'], brand['nome'])
        yield brand_data

class ExtractionResult(TypedDict):
    brand: list[dict[str, str]]
    models: list[dict[str, str]]
    years: list[dict[str, str]]
    data: list[dict[str, str]]

class BrandExtractor:
    def __init__(self, brand: Brand, limit: int = -1) -> None:
        """
        Configure o limit para especificar o número máximo de resultados
        a serem extraídos da API, caso não queira aguardar o tempo de extrair tudo.

        Padrão: -1 (ilimitado)
        """

        self.__brand = brand
        self.__models_queue: asyncio.Queue[Model | None] = asyncio.Queue()
        self.__years_queue: asyncio.Queue[Year | None] = asyncio.Queue()
        self.__limit = limit

        self.__model_buffer: list[dict] = list()
        self.__year_buffer: list[dict] = list()
        self.__data_buffer: list[dict] = list()

    async def __async_request(self, url: str, max_retries: int = 5, base_delay=5.0, max_delay=20.0, jitter=2.0):
        retries = 0

        while retries < max_retries:
            async with aiohttp.ClientSession() as session:
                # Faz a requisição e em caso de erro (rate limit) faz as retentativas
                # utilizando um backoff exponencial entre elas
                try:
                    async with session.get(url, timeout=30) as response:
                        data = await response.text()

                        if response.status < 400:
                            return response, data

                        else:
                            raise aiohttp.ClientError(f"Failed to extract models for {self.__brand.name} from api due to an exception: {data}")

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"Failed to request {url}. Retrying for {retries+1}")
                    delay = min(max_delay, base_delay * 2 ** retries)
                    sleep_time = delay + random.uniform(0, jitter)
                    
                    retries += 1
                    time.sleep(sleep_time)

        print(f"All attempts to request {url} failed and the retries has been exhausted")
        return None, None
        
    async def _extract_models(self):
        url = BASE_URL+F'/marcas/{self.__brand.id}/modelos'
        print(f"Extracting models from url {url}")
        response, data = await self.__async_request(url)

        if not response and not data:
            raise RuntimeError(f"Failed to extract models for {self.__brand.name} from api due to an exception: {data}")

        # if response.status >= 400:
        #     raise RuntimeError(f"Failed to extract models for {self.__brand.name} from api due to an exception: {data}")
        
        models: list[dict[str, str]] = json.loads(data)['modelos']

        for model in models:
            # Insere os dados do modelo extraído na fila de modelos
            model_data = Model(self.__brand, str(model['codigo']), model['nome'])
            await self.__models_queue.put(model_data)

        # Envia um sinal para fechar a fila de modelos
        await self.__models_queue.put(None)

    async def _extract_years(self):
        model = await self.__models_queue.get()
        self.__model_buffer.append(model.to_dict())

        while model:
            url = BASE_URL+F'/marcas/{model.brand.id}/modelos/{model.id}/anos'
            print(f"Extracting years from url {url}")
            response, data = await self.__async_request(url)

            if not response and not data:
                raise RuntimeError(f"Failed to extract years for {model.brand.name} {model.name} from api due to an exception: {data}")

            # if response.status >= 400:
            #     raise RuntimeError(f"Failed to extract years for {model.brand.name} {model.name} from api due to an exception: {data}")
            
            years: list[dict[str, str]] = json.loads(data)

            for year in years:
                # Insere os dados do ano extraído na fila de anos
                year_data = Year(model, str(year['codigo']), year['nome'])
                await self.__years_queue.put(year_data)

            # Encerra a extração de anos se tiver alcançado o limite de dados no buffer principal
            if self.__limit >= 0 and len(self.__data_buffer) >= self.__limit:
                break
            
            model = await self.__models_queue.get()

            # Salva o modelo no buffer de modelos
            if model:
                self.__model_buffer.append(model.to_dict())
        
        # Envia um sinal para fechar a fila de anos
        await self.__years_queue.put(None)

    async def _extract_all_data(self):
        year = await self.__years_queue.get()
        self.__year_buffer.append(year.to_dict())

        while year:
            url = BASE_URL+F'/marcas/{year.model.brand.id}/modelos/{year.model.id}/anos/{year.id}'
            print(f"Extracting data from url {url}")
            response, data = await self.__async_request(url)

            if not response and not data:
                raise RuntimeError(f"Failed to extract data for {year.model.brand.name} {year.model.name} {year.name} from api due to an exception: {data}")
            
            # if response.status >= 400:
            #     raise RuntimeError(f"Failed to extract data for {year.model.brand.name} {year.model.name} {year.name} from api due to an exception: {data}")
            
            data: dict[str, Any] = json.loads(data)

            # Converte o campo de valor para float

            value_pattern = r"R\$\s*([\d.,]+)"
            match = re.search(value_pattern, data['Valor'])
            
            if not match:
                raise RuntimeError(f"Unexpected response for value field: {data['Valor']}")
            
            value_str = match.group(1).replace(".", "").replace(",", ".")
            value = float(value_str)

            # Converte o campo de mês de referência para o formato MM-YYYY
            months = {
                "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
            }

            ref_month: str = data['MesReferencia']
            ref_month_splitted = ref_month.split(" ")

            if not ref_month_splitted[0] in months:
                raise RuntimeError(f"Unexpected entry for month reference: {ref_month}")

            ref_month_number = months[ref_month_splitted[0]]
            ref_month_formated = f"{ref_month_number}-{ref_month_splitted[-1]}"
            
            result = {
                'type': data['TipoVeiculo'],
                'value': value,
                'brand': year.model.brand.name,
                'model': year.model.name,
                'year': year.name,
                'fuel': data['Combustivel'],
                'id': data['CodigoFipe'],
                'month_reference': ref_month_formated,
                'fuel_sign': data['SiglaCombustivel']
            }

            # Salva os detalhes do veículo no buffer
            self.__data_buffer.append(result)

            # Encerra a extração dos dados se tiver alcançado o limite de dados no buffer principal
            if self.__limit >= 0 and len(self.__data_buffer) >= self.__limit:
                break

            year = await self.__years_queue.get()

            if year:
                # Salva o ano no buffer de anos
                self.__year_buffer.append(year.to_dict())
    
    async def stream(self):
        # Executa concorrentemente as extrações de dados
        models = self._extract_models()
        years = self._extract_years()
        data = self._extract_all_data()

        self.future = asyncio.gather(models, years, data)
        await self.future

        result = ExtractionResult(
            brand=[self.__brand.to_dict()],
            models=self.__model_buffer,
            years=self.__year_buffer,
            data=self.__data_buffer
        )

        return result