# src/app/core/system.py
from fastapi import HTTPException, status
import httpx
import asyncio
from typing import List, Dict, Optional
import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Address, User
from src.app.utils.cache import UserCache


class AddressService:
    def __init__(self, db: AsyncSession):
        self.NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
        self.MAX_RESULTS = 5
        self.MIN_QUERY_LENGTH = 2
        self.db = db
        self.headers = {
            'User-Agent': 'Atatek Family Tree/1.0'
        }
        self.cache = UserCache()

    async def search_locations(self, query: str) -> List[Dict]:
        """
        Поиск локаций по запросу
        1. Сначала ищем в БД
        2. Если не нашли - делаем запрос к Nominatim
        """
        if len(query) < self.MIN_QUERY_LENGTH:
            logging.info(f"Query too short: {query}")
            return []

        # Начинаем поиск
        logging.info(f"Starting location search for query: {query}")

        # Поиск в БД
        db_results = await self._search_in_db(query)
        if db_results:
            logging.info(f"Found {len(db_results)} results in database")
            return db_results[:self.MAX_RESULTS]
        else:
            logging.info("No results found in database, searching with Nominatim")

        # Поиск через Nominatim
        nominatim_results = await self._search_nominatim(query)
        if nominatim_results:
            logging.info(f"Found {len(nominatim_results)} results from Nominatim")

            # Добавляем маркер источника для всех результатов
            for result in nominatim_results:
                result['source'] = 'nominatim'

            # Сохраняем результаты в БД
            saved_results = await self._save_to_db(nominatim_results)

            # Проверяем, что у нас есть сохраненные результаты
            if saved_results:
                logging.info(f"Successfully saved {len(saved_results)} results to database")
                return saved_results[:self.MAX_RESULTS]
            else:
                logging.warning("Failed to save results to database, returning original Nominatim results")
                return nominatim_results[:self.MAX_RESULTS]
        else:
            logging.info("No results found from Nominatim")

        return []

    async def _search_in_db(self, query: str) -> List[Dict]:
        """Поиск в локальной БД"""
        results = []

        try:
            # Поиск по релевантным полям адреса
            stmt = select(Address).where(
                or_(
                    Address.name.ilike(f"%{query}%"),
                    Address.display_name.ilike(f"%{query}%")
                )
            )

            result = await self.db.execute(stmt)
            locations = result.scalars().all()

            # Логируем количество найденных результатов для отладки
            logging.info(f"Found {len(locations)} locations in database for query: {query}")

            for loc in locations:
                results.append({
                    'id': loc.id,
                    'osm': loc.osm,
                    'name': loc.name,
                    'address_type': loc.address_type,
                    'latitude': loc.lat,
                    'longitude': loc.lon,
                    'display_name': loc.display_name,
                    'source': 'database'  # Маркер источника данных
                })

        except Exception as e:
            logging.error(f"Error searching in database: {str(e)}")
            # Вместо того чтобы упасть, просто возвращаем пустой результат

        return results

    async def _search_nominatim(self, query: str) -> List[Dict]:
        """Поиск через Nominatim API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'addressdetails': 1,
                'limit': self.MAX_RESULTS
            }

            logging.info(f"Querying Nominatim with: {query}")

            # Используем httpx для асинхронных HTTP-запросов
            async with httpx.AsyncClient(timeout=10.0) as client:  # Увеличиваем таймаут
                response = await client.get(
                    self.NOMINATIM_URL,
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()

            # Добавляем задержку для соблюдения лимитов API
            await asyncio.sleep(1)

            # Получаем данные JSON
            data = response.json()
            logging.info(f"Received {len(data)} results from Nominatim")

            if not data:
                logging.info("No results returned from Nominatim")
                return []

            results = []
            for item in data:
                # Логируем тип результата для отладки
                item_type = item.get('type', 'unknown')
                item_id = item.get('osm_id', 'unknown')
                logging.debug(f"Processing Nominatim result: type={item_type}, id={item_id}")

                address = item.get('address', {})
                # Извлекаем компоненты адреса
                location = self._parse_nominatim_address(item, address)
                if location:
                    location.update({
                        'latitude': float(item['lat']),
                        'longitude': float(item['lon'])
                    })
                    results.append(location)
                else:
                    logging.debug(
                        f"Skipping item due to incomplete address data: {item.get('display_name', 'unknown')}")

            logging.info(f"Successfully parsed {len(results)} locations from Nominatim")
            return results

        except httpx.HTTPError as e:
            logging.error(f"Nominatim API error: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error during Nominatim search: {str(e)}")
            return []

    def _parse_nominatim_address(self, item: Dict, address: Dict) -> Optional[Dict]:
        """Парсинг адреса из Nominatim в наш формат"""
        try:
            # Получаем идентификатор OSM
            osm_id = None
            # Приоритет отдаем osm_id, затем place_id
            if 'osm_id' in item and item['osm_id']:
                osm_id = str(item['osm_id'])
            elif 'place_id' in item and item['place_id']:
                osm_id = f"place_{item['place_id']}"

            # Если нет никакого ID, генерируем хеш на основе координат
            if not osm_id:
                lat = item.get('lat', '')
                lon = item.get('lon', '')
                if lat and lon:
                    osm_id = f"coord_{lat}_{lon}"
                else:
                    # Если нет ID и координат, пропускаем
                    logging.warning(f"No osm_id or coordinates for item: {item.get('display_name', 'unknown')}")
                    return None

            # Получаем тип адреса
            address_type = item.get('type', 'unknown')

            # Определяем основное имя из различных полей
            name_candidates = [
                address.get('city'),
                address.get('town'),
                address.get('village'),
                address.get('hamlet'),
                address.get('suburb'),
                address.get('neighbourhood'),
                item.get('name')
            ]
            # Берем первое непустое значение
            name = next((n for n in name_candidates if n), "Unnamed location")

            # Используем display_name из ответа
            display_name = item.get('display_name', '')

            # Формируем результат
            return {
                'osm': osm_id,
                'name': name,
                'address_type': address_type,
                'display_name': display_name
            }

        except Exception as e:
            logging.error(f"Error parsing Nominatim address: {str(e)}")
            logging.error(f"Problematic item: {item}")
            return None

    async def _save_to_db(self, locations: List[Dict]) -> List[Dict]:
        """Сохранение локаций в БД"""
        saved_locations = []

        for loc_data in locations:
            try:
                # Проверяем, существует ли уже такая локация по osm id
                stmt = select(Address).where(Address.osm == loc_data['osm'])
                result = await self.db.execute(stmt)
                existing = result.scalars().first()

                if existing:
                    # Формируем данные из существующей записи
                    saved_locations.append({
                        'id': existing.id,
                        'osm': existing.osm,
                        'name': existing.name,
                        'address_type': existing.address_type,
                        'latitude': existing.lat,
                        'longitude': existing.lon,
                        'display_name': existing.display_name
                    })
                    continue

                # Создаем новую локацию
                new_location = Address(
                    osm=loc_data['osm'],
                    name=loc_data['name'],
                    address_type=loc_data['address_type'],
                    lat=loc_data['latitude'],
                    lon=loc_data['longitude'],
                    display_name=loc_data['display_name']
                )

                # Добавляем и делаем коммит
                self.db.add(new_location)
                await self.db.commit()
                await self.db.refresh(new_location)  # Обновляем объект после сохранения

                # Формируем результат из новой записи
                saved_locations.append({
                    'id': new_location.id,
                    'osm': new_location.osm,
                    'name': new_location.name,
                    'address_type': new_location.address_type,
                    'latitude': new_location.lat,
                    'longitude': new_location.lon,
                    'display_name': new_location.display_name
                })

            except Exception as e:
                await self.db.rollback()
                logging.error(f"Error processing location: {str(e)}")
                # Логируем больше информации для отладки
                logging.error(f"Location data: {loc_data}")

        # Проверяем, что есть результаты
        if not saved_locations and locations:
            logging.warning(f"No locations were saved from {len(locations)} potential matches")

        return saved_locations
    
    async def set_or_update_address(self, user_id: int, address_id: int):
        stmp = await self.db.execute(select(User).where(User.id == user_id))
        user = stmp.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Қолданушы табылмады')
        user.address_id = address_id
        await self.db.commit()
        await self.db.refresh(user)
        await self.cache.invalidate(user_id)
        return {
            "detail": "Қолданушының мекен жайы сәтті ауыстырылды"
        }