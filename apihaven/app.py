from typer import Typer, Option
from apihaven import APPNAME, VERSION, utils
from rich import print, table, console
from typing import Optional, List
import typer
import json
app = Typer()

def _callback(value:bool):
    apihaven_text = """
 ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░░▒▓█▓▒▒▓█▓▒░░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██▓▒░  ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                                                                                                 
                                                                                        
"""
    print(apihaven_text)
    if value:

        typer.secho(f"v{VERSION}", fg="blue")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = Option(None, "--version","-v", help="Show Application's Version",is_eager=True,callback=_callback )
):

    return



@app.command(name="authenticate")
def authenticate(
    username:str= typer.Option(...,"--username","-u",help="Username"),
    email:Optional[str] = typer.Option(None,"--email", "-e", help='Email'),
    password:str = Option(..., "--password","-p", help="Password"),
):
    try:
        if utils.authenticate_user(username, password):
            typer.secho("Authenticated ✅", fg="green")
        else:
            typer.secho("Authentication Error", fg="red")
    except Exception as e:
        typer.secho(f"Error: {e.args}", fg="red")
    raise typer.Exit()

def parse_key_value_pairs(pairs: List[str]) -> dict:
    result = {}
    for pair in pairs:
        if '=' not in pair:
            raise typer.BadParameter(f"Invalid format for pair: '{pair}'. Expected format: key=value")
        key, value = pair.split('=', 1)
        result[key] = value
    return result

@app.command(name="resource", help="Manage resources created by user")
def resource_management(
    update_:bool = Option(False, "--update","-ur",help="Update A Resource"),
    delete_:bool = Option(False, "--delete","-d",help="Delete A Resource"),
    create_:bool = Option(False, "--create", "-c", help="Create New Resource" ),
    add_:bool = Option(False, "--add","-a",help="Add resource"),
    username:str = Option(..., '--username','-u', help='username'),
    get_:bool = Option(False, "--get","-g",help="Get resource"),
    resource_name:Optional[str] = Option(None, '--resource','-r', help='resource'),
    data:str = Option("","--data","-dr",help="Resource data for creation, or update")
):
    """
    Windows = "{""name"":""Test2"",""columns"":[{""name"":""NAME"",""type"":""str"",""constraint"":""NOTNULL""}]}"
    Others = '{"name":"Test2","columns":[{"name":"NAME","type":"str","constraint":"NOTNULL"}]}'

    data__create = "{""name"": ""census"",""columns"": [ {""name"": ""name"", ""type": ""str"", ""constraint"": ""not null""},{""name"": ""sex"", ""type"": ""str"", ""constraint"": ""not null""},{""name"":""house_number"",""type"":""str"",""constraint"":""not null""},{""name"": ""age"", ""type"": ""int"", ""constraint"": ""not null""},{""name"":""height"",""type"":""float"",""constraint"":""null""}]}
    data__add = "{""resource"": ""census"",""data"": [ [{""column_name"":""name"",""value"":""User Name""},{""column_name"":""sex"",""value"":""f""},{""column_name"":""house_number"",""value"":""AU-00005-4138""},{""column_name"":""age"",""value"":24},{""column_name"":""height"",""value"":1.7} ]]}"
    """
 
    
    
    if create_:
        utils.create_resource(username=username, data=data)
    elif get_:
        if resource_name:
            utils.get_resource(username=username, name=resource_name)
        else:
            utils.get_resource(username=username)
    elif add_:
        utils.add_data(username=username, data=data)
    raise typer.Exit()
    

@app.command("login")
def login_user(username:str = Option(..., "--username","-u", help="Username"), password:str = Option(..., "--password","-p",help="Password")):
    if utils.login(username, password):
        print(f"[green]Hello, {username}![/green]")
    raise typer.Exit()