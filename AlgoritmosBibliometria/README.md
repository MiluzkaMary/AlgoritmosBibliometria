# Proyecto Bibliometría

## Requisitos previos

1. **Instalar Python**: Asegúrate de tener Python instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).

## Configuración del entorno virtual

1. **Crear un entorno virtual**:
    ```sh
    python -m venv venv
    ```

2. **Activar el entorno virtual**:

    - En Command Prompt:
        ```sh
        venv\Scripts\activate.bat
        ```

    - En PowerShell(a mi me sirvio este):
        ```sh
        venv\Scripts\Activate.ps1
        ```

    - En Git Bash o WSL:
        ```sh
        source venv/Scripts/activate
        ```

3. **Instalar dependencias**:
    Asegúrate de tener un archivo `requirements.txt` con las siguientes dependencias:
    ```txt
    undetected-chromedriver
    selenium
    aiohttp
    lxml
    ```

    Luego, instala las dependencias ejecutando:
    ```sh
    pip install -r requirements.txt
    ```

## Ejecución del scraper

1. **Ejecutar el scraper**:
    ```sh
    python scraper.py
    ```

## Ejecución de [main.py](http://_vscodecontentref_/2)

1. **Ejecutar [main.py](http://_vscodecontentref_/3)**:
    ```sh
    python main.py
    ```

Asegúrate de que el entorno virtual esté activado antes de ejecutar los scripts. Esto garantizará que las dependencias necesarias estén disponibles.