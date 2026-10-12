from shared.json_manager import GestorJSON


def prueba():
    gestor = GestorJSON("data/clientes.json")
    datos = gestor.leer()
    print("Prueba de lectura de GestorJSON:")
    print(datos)


if __name__ == "__main__":
    prueba()
