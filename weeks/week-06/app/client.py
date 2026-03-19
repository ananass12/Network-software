import json
import requests
from typing import Dict, Any, Optional, List

project_code = "s18"

def build_payload(query: str, variables: dict) -> dict:
    """
    Формирует словарь для отправки GraphQL запроса.
    
    :param query: Текст запроса (query или mutation).
    :param variables: Словарь с переменными.

    """
    return {
        "query": query,
        "variables": variables or {} 
    }

class GraphQLClient:
    def __init__(self, endpoint: str = "http://nginx/graphql"):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
    
    def execute(self, query: str, variables: dict = None) -> Dict[str, Any]:
        """Основной метод выполнения запросов"""
        payload = build_payload(query, variables or {})
        print(f"Запрос: {json.dumps(payload, indent=2)}")
          
        response = self.session.post(self.endpoint, json=payload, timeout=10)
        result = response.json()
          
        print(f"Ответ: {json.dumps(result, indent=2)}")
          
        if "errors" in result:
            print("Ошибки:", [e["message"] for e in result["errors"]])
          
        return result
    
    def get_tickets(self) -> List[Dict[str, Any]]:
        query = """ query { getAllTickets { id status } } """
        result = self.execute(query) 
        return result.get("data", {}).get("getAllTickets", [])
    
    def create_ticket(self, status: str) -> Optional[Dict[str, Any]]:
        query = """ mutation CreateTicket($status: String!) {createTicket(input: {status: $status}) { id status }} """
        result = self.execute(query, {"status": status})  
        return result.get("data", {}).get("createTicket")

if __name__ == "__main__":
    print("GraphQL Клиент запущен\n")
    client = GraphQLClient()

    print("1. Получаем все билеты:\n")
    tickets = client.get_tickets()
    
    print("\n2. Создаём новый билет:\n")
    new_ticket = client.create_ticket("high priority")
    
    print("\n3. Проверяем список после создания:\n")
    all_tickets = client.get_tickets()
    
    print(f"\n4. Всего билетов: {len(all_tickets)}")