import os
import json
import sqlite3
import requests
import keyring
from rich import print
from rich.table import Table
from rich.console import Console
from apihaven import APPNAME

# Environment configuration
DB_PATH = os.environ.get('DB_PATH', '')
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000/app')


def save_token(token: dict, username: str):
    """Stores the user's auth token using the system keyring."""
    keyring.set_password(APPNAME, username, json.dumps(token))


def load_token(username: str):
    """Loads the user's auth token from the system keyring."""
    token = keyring.get_password(APPNAME, username)
    
    return json.loads(token) if token else None


def delete_token(username: str):
    """Deletes the user's token from the system keyring."""
    keyring.delete_password(APPNAME, username)


def refresh_token(refresh_token: str) -> str:
    """Refreshes the access token using the provided refresh token."""
    endpoint = f"{BASE_URL}/token/refresh"
    payload = {"refresh": refresh_token}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code in (401, 403):
        raise requests.HTTPError("Invalid Token. Try Login")
    data = response.json()

    if 'access' in data:
        return data['access']

def login(username:str, password:str):
    url = f"{BASE_URL}/token/"
    payload = json.dumps({"username":username, "password":password})
    headers = {"Content-Type":"application/json"}
    response = requests.post(url,data=payload, headers=headers )
    res_data = response.json()
    if res_data.get('access'):
        save_token(res_data, username)
        return True
    else:
        raise ValueError("Invalid User Credentials.")


def authenticate_user(username: str, password: str) -> bool:
    """Authenticates or signs up the user and stores the token securely."""
    try:
        token_data = load_token(username)
        if not token_data:
            # First-time login or signup
            credentials = {"username": username, "password": password}
            headers = {'Content-Type': 'application/json'}

            res = requests.post(f"{BASE_URL}/token/", json=credentials, headers=headers)
            data = res.json()

            if 'access' in data:
                save_token(data, username)
                return True

            # Attempt signup
            res = requests.post(f"{BASE_URL}/signup", json=credentials, headers=headers)
            data = res.json()

            if 'access' in data:
                save_token(data, username)
                return True

            raise ValueError(data.get('error', 'Signup failed.'))

        # Refresh token if token exists
        access = refresh_token(token_data['refresh'])
        save_token({'refresh': token_data['refresh'], 'access': access}, username)
        return True

    except Exception as e:
        print(f"[bold red]Authentication Error:[/bold red] {e}")
        return False


def get_resource(username: str, name: str = '') -> bool:
    """
    Retrieves or creates a resource for the user and displays it in a rich table.

    Args:
        username (str): Username of the user.
        name (str, optional): Resource name to filter by.

    Returns:
        bool: Success status.
    """
    token_data = load_token(username)
    if not token_data:
        print("[red]Token not found. Please authenticate first.[/red]")
        return False

    try:
        access = refresh_token(token_data['refresh'])
    except Exception as e:
        print(f"[red]Token refresh failed:[/red] {e}")
        return False

    query = f"?name={name}" if name else ""
    endpoint = f"{BASE_URL}/resource/{query}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access}"
    }

    response = requests.get(endpoint, headers=headers)
    res_data = response.json()

    if res_data.get('results'):
        data = res_data['results']['data']
        console = Console()
        for table_ in data:
        
            table = Table(title=table_.get('name','unknown'))
            table_data = table_.get('data')
            if len(table_data) < 1:
                print(f"[yellow]Resource {table.title} has no Rows[/yellow]")
                continue
            columns = [str(i) for i in table_data[0].keys()]
            for key in columns:
                    table.add_column(str(key))
            for row in table_data:   
                    table.add_row(*(str(row.get(key, '')) for key in columns))

            console.print(table)
        return True
    elif res_data.get('success'): 
        """
        {
    'success': True,
    'data': {
        'resource_id': '563e7d4a-6ba2-4ad3-8092-95fd32ab88cb',
        'name': 'mydata',
        'columns': [
            {'name': 'age', 'type': 'int', 'constraint': 'NOT NULL'},
            {'name': 'name', 'type': 'str', 'constraint': 'NULL'},
            {'name': 'score', 'type': 'float', 'constraint': 'NOT NULL'}
        ],
        'data': [{'age': 25, 'name': 'John', 'score': 25.0}, {'age': 30, 'name': 'Jane', 'score': 15.0}]
    }
}
        """
        table_data = res_data.get('data',{'data':[]}).get('data')
        if len(table_data) < 1:
            print(f"[yellow]No Rows for Resource {name}[/yellow]")
            return True
        else:
            console = Console()
            table = Table(title=res_data.get('data',{'name':'unknown'}).get('name'))
            columns = table_data[0].keys()
            [table.add_column(str(i)) for i in columns]
            for row in table_data:   
                table.add_row(*(str(row.get(key, '')) for key in columns))
            console.print(table)  
            return True         

    print(res_data)
    print(f"[red]{res_data.get('message', 'Failed to fetch resource.')}[/red]")
    return False


def create_resource(username:str, data:dict):
    """
    Args:
        username (str): Username of user.
        data (dict): Resource defiition.
            Example:
                    {
                        "name": "mydata",
                        "columns": [
                            {"name": "age", "type": "int", "constraint": "not null"},
                            {"name": "name", "type": "str", "constraint": "null"},
                            {"name": "score", "type": "float", "constraint": "not null"}
                        ]
                    }
    """
    token = load_token(username)
    if not token:
        print("[red]Token not found. Please authenticate first.[/red]")
        return False
    access = refresh_token(token['refresh'])
    url = f"{BASE_URL}/resource/"
    headers = {"Content-Type":"application/json", "Authorization":f"Bearer {access}"}
    res = requests.post(url, data=data, headers=headers)
    res_data = res.json()
    if res_data.get('success'):
        return True
    else:
        print(f"[red]{res_data.get('message')}[/red]")
        return False

def add_data(username:str, data:dict):
    token_data = load_token(username)
    if not token_data:
        print("[red]Token not found. Please authenticate first.[/red]")
        return False

    try:
        access = refresh_token(token_data['refresh'])
    except Exception as e:
        print(f"[red]Token refresh failed:[/red] {e}")
        return False

    endpoint = f"{BASE_URL}/resource/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access}"
    }

    response = requests.put(endpoint, headers=headers, data=data)
    res_data = response.json()
    if res_data.get('success'):
        print(f"Data added to {json.loads(data)['resource']}")
        return True
    print(f"[red]{res_data.get('message')}[/red]")
    return False