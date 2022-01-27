from abc import ABC, abstractmethod

from redis import Redis


class AbstractDatabaseProxy(ABC):
    """
        Для удобной работы с ДБ.
        Можно в любой момент надёжно изменить ДБ или логику работы, унаследовав этот класс
    """

    @abstractmethod
    def add_values_in_set(self, key: str, *values) -> None:
        pass
    
    @abstractmethod
    def get_unique_values_by_timerange(self, start: int, end: int) -> set[str]:
        pass

    @abstractmethod
    def flush_db(self):
        pass



class RedisDatabaseProxy(AbstractDatabaseProxy):
    """
        Логика работы с Redis
    """
    
    def __init__(self, database: Redis, prefix: str = ""):
        self._database = database
        self._prefix = prefix
    

    def enable_test_mode(self):
        self._prefix = "test:"
        
    def build_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def unbuild_key(self, key: str) -> str:
        return key.replace(self._prefix, "")

    def add_values_in_set(self, key: str, *values) -> None:
        """
            Добавляет значения в множество,
            если множества нет, то redis сам его создаст
        """
        
        self._database.sadd(self.build_key(key), *values)
    
    def get_unique_values_by_timerange(self, start: int, end: int) -> set[str]:
        """
            Возвращает уникальные записи по ключу unix_time
        """
        
        domains = set()

        str_start, str_end = str(start), str(end)
        len_start, len_end = len(str_start), len(str_end)
        
        # Ищем схожесть, чтобы не просматривать все ключи Redis
        # Например, start=1999123 end=1999666
        # pattern будет равен "1999*", так как нам нужны ключи, которые начинаются только так
        # если start = 200, end = 100, то pattern будет "*"
        pattern = ""
        for i in range(min(len_start, len_end)):
            if str_start[i] == str_end[i]:
                pattern += str_start[i]
            else:
                break
        pattern += "*"
        
        for key in self._database.scan_iter(self.build_key(pattern)):
            try:
                int_key = int(self.unbuild_key(key))
            except ValueError:
                continue
            if int_key > start and int_key < end:
                domains_set = self._database.smembers(key)
                for domain in domains_set:
                    domains.add(domain)
        return domains
        

    def flush_db(self) -> None:
        keys = self._database.keys(self.build_key("*"))
        if keys != []:
            self._database.delete(*keys)
        
