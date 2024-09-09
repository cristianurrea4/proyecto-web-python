from app import app

if __name__ == "__main__":
    # El debug=True hace que cada vez que reiniciamos el servidor o modifiquemos código el servidor de Flask se reinicie solo.
    app.run(debug=True)

