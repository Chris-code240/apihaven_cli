from pathlib import Path
from typing import List, Optional
import typer
from apihaven import (__app_name__, __version__, database, SUCCESS)


app = typer.Typer()
User = database.User
db = database.SessionLocal()

def _version_callback(value: bool) -> None:
    if value:
        typer.secho(f"{__app_name__} v{__version__}", fg="blue")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


@app.command(name="signup")
def signup(
    username:str = typer.Option(..., prompt=True, help="Username"),
    email:str = typer.Option(..., prompt=True, help="Email"),
    full_name:str = typer.Option(..., prompt=True, help="Full name"),
    password:str = typer.Option(..., prompt=True, help="Password", hide_input=True),
    confirm_password:str = typer.Option(..., prompt=True, help="Confirm Password", hide_input=True),
):

    if password != confirm_password:    
        typer.secho(f"Password mismatched.", fg="red")
        raise typer.Exit()
    

    try:
        username = username.lower()
        existing_user = db.query(User).filter(User.username == username).first()

        if existing_user:
            typer.secho(f"User with the username {username} already exist", fg="red")
            raise typer.Exit()
        # Create new user
        new_user = User(username=username, email=email, full_name=full_name)
        new_user.set_password(password)  # Hash and set the password
        db.add(new_user)
        db.commit()

        typer.secho("Signup successful!", fg="green")

    except Exception as e:
        typer.secho(f"Error: {str(e)}", fg="red")
    finally:
        db.close()  


@app.command(name="init")
def db_init():
    try:
        database.init_db()
        typer.secho(f"DB Configured", fg="blue")
        raise typer.Exit(SUCCESS)  
    except Exception as e:
        typer.secho(f"Error: {str(e)}", fg="red")
        raise typer.Exit()


@app.command(name="login")
def user_login(
    username:str = typer.Option(..., help="Username", prompt=True),
    password:str = typer.Option(..., help="Password", prompt=True, hide_input=True)
):
    user = db.query(User).filter(User.username == username.lower()).first()
    if not user:
        typer.secho(f"User does not exist", fg="red")
        raise typer.Exit(SUCCESS)

    if user and user.check_password(raw_password=password):
        typer.secho(f"Logged in", fg="green")
        raise typer.Exit()
    else:
        typer.secho(f"Invalid Password", fg="red")
        raise typer.Exit()



    